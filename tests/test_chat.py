"""Tests for chat/AI functionality"""

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.ai.intent_parser import IntentParser
from app.ai.assistant import TammyAssistant
from app.database import Base
from app.services.appointment_service import AppointmentService
from app.services.task_service import TaskService
from app.services.contact_service import ContactService
from app.utils.default_user import DEFAULT_USER_ID


async def _make_test_db():
    """A throwaway in-memory SQLite database for a single test"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return engine, async_sessionmaker(engine, expire_on_commit=False)


class TestIntentParser:
    """Test intent parsing"""

    def test_schedule_appointment_intent(self):
        """Test appointment scheduling intent detection"""
        message = "Schedule a meeting with John tomorrow at 2pm"
        parsed = IntentParser.parse(message)

        assert parsed["intent"] == "schedule_appointment"
        assert "names" in parsed["entities"]
        assert "John" in parsed["entities"]["names"]

    def test_check_calendar_intent(self):
        """Test calendar check intent detection"""
        message = "What's on my calendar today?"
        parsed = IntentParser.parse(message)

        assert parsed["intent"] == "check_calendar"

    def test_create_task_intent(self):
        """Test task creation intent detection"""
        message = "Remind me to call Sarah on Friday"
        parsed = IntentParser.parse(message)

        assert parsed["intent"] == "create_task"
        assert "names" in parsed["entities"]

    def test_time_extraction(self):
        """Test time extraction from message"""
        message = "Schedule a meeting at 3:30pm tomorrow"
        parsed = IntentParser.parse(message)

        assert "time" in parsed["entities"]
        assert "date" in parsed["entities"]


@pytest.mark.asyncio
class TestTammyAssistant:
    """Test Tammy assistant"""

    async def test_process_message(self):
        """Test message processing"""
        engine, session_maker = await _make_test_db()
        try:
            async with session_maker() as db:
                assistant = TammyAssistant()
                response = await assistant.process_message("What appointments do I have today?", db)

                assert response["response"] is not None
                assert response["intent"] is not None
                assert isinstance(response["confidence"], float)
        finally:
            await engine.dispose()

    async def test_conversation_history(self):
        """Test conversation history tracking"""
        engine, session_maker = await _make_test_db()
        try:
            async with session_maker() as db:
                assistant = TammyAssistant()
                await assistant.process_message("Hello", db)

                history = assistant.get_history()
                assert len(history) == 2  # User + Assistant

                assistant.clear_history()
                assert len(assistant.get_history()) == 0
        finally:
            await engine.dispose()

    async def test_schedule_appointment_creates_real_appointment(self):
        """Scheduling an appointment should actually persist one, not just describe it"""
        engine, session_maker = await _make_test_db()
        try:
            async with session_maker() as db:
                assistant = TammyAssistant()
                response = await assistant.process_message(
                    "Schedule a meeting with John tomorrow at 2pm", db
                )
                assert response["intent"] == "schedule_appointment"
                assert response["actions"]
                assert response["actions"][0]["type"] == "appointment_created"

            async with session_maker() as db:
                appointments = await AppointmentService.get_user_appointments(db, DEFAULT_USER_ID)
                assert len(appointments) == 1
                assert "John" in appointments[0].title
                assert appointments[0].start_time.hour == 14
        finally:
            await engine.dispose()

    async def test_create_task_creates_real_task(self):
        """Creating a task should actually persist one, not just describe it"""
        engine, session_maker = await _make_test_db()
        try:
            async with session_maker() as db:
                assistant = TammyAssistant()
                response = await assistant.process_message("Remind me to call Sarah on Friday", db)
                assert response["intent"] == "create_task"
                assert response["actions"][0]["type"] == "task_created"

            async with session_maker() as db:
                tasks = await TaskService.get_user_tasks(db, DEFAULT_USER_ID)
                assert len(tasks) == 1
                assert "sarah" in tasks[0].title.lower()
        finally:
            await engine.dispose()

    async def test_add_contact_creates_real_contact(self):
        """Adding a contact should actually persist one, not just describe it"""
        engine, session_maker = await _make_test_db()
        try:
            async with session_maker() as db:
                assistant = TammyAssistant()
                response = await assistant.process_message(
                    "Add contact Jane Smith jane.smith@example.com", db
                )
                assert response["intent"] == "add_contact"
                assert response["actions"][0]["type"] == "contact_created"

            async with session_maker() as db:
                contacts = await ContactService.get_user_contacts(db, DEFAULT_USER_ID)
                assert len(contacts) == 1
                assert contacts[0].first_name == "Jane"
                assert contacts[0].email == "jane.smith@example.com"
        finally:
            await engine.dispose()

    async def test_schedule_appointment_without_time_asks_for_clarification(self):
        """Without a date+time, nothing should be created yet"""
        engine, session_maker = await _make_test_db()
        try:
            async with session_maker() as db:
                assistant = TammyAssistant()
                response = await assistant.process_message("Schedule a meeting with John", db)
                assert response["actions"] == []

                appointments = await AppointmentService.get_user_appointments(db, DEFAULT_USER_ID)
                assert len(appointments) == 0
        finally:
            await engine.dispose()

    async def test_follow_up_with_session_id_resumes_pending_intent(self):
        """A reply that only supplies the missing date/time should finish the
        original request, not be parsed as a brand-new, context-free message.

        Without a session_id (the previous test above), this correctly has
        no way to remember "with John" for a later message - that's the
        expected, documented limit of a stateless call. With one, Tammy
        should actually remember.
        """
        engine, session_maker = await _make_test_db()
        session_id = "test-session-mike"
        try:
            async with session_maker() as db:
                assistant = TammyAssistant()
                response = await assistant.process_message(
                    "Schedule a meeting with Mike", db, session_id=session_id
                )
                assert response["actions"] == []
                assert response["intent"] == "schedule_appointment"

            async with session_maker() as db:
                assistant = TammyAssistant()
                response = await assistant.process_message(
                    "Tomorrow at 2pm", db, session_id=session_id
                )
                assert response["intent"] == "schedule_appointment"
                assert response["actions"]
                assert response["actions"][0]["type"] == "appointment_created"

            async with session_maker() as db:
                appointments = await AppointmentService.get_user_appointments(db, DEFAULT_USER_ID)
                assert len(appointments) == 1
                assert "Mike" in appointments[0].title
                assert appointments[0].start_time.hour == 14
        finally:
            await engine.dispose()

    async def test_unrelated_follow_up_abandons_pending_intent(self):
        """If the next message is clearly a different, recognized request,
        it should be handled on its own - not merged into the stale
        pending one, and the stale one shouldn't resurface later either.
        """
        engine, session_maker = await _make_test_db()
        session_id = "test-session-abandon"
        try:
            async with session_maker() as db:
                assistant = TammyAssistant()
                response = await assistant.process_message(
                    "Schedule a meeting with Mike", db, session_id=session_id
                )
                assert response["actions"] == []

            async with session_maker() as db:
                assistant = TammyAssistant()
                response = await assistant.process_message(
                    "Create a task to call Jane", db, session_id=session_id
                )
                assert response["intent"] == "create_task"
                assert response["actions"][0]["type"] == "task_created"

            async with session_maker() as db:
                # The abandoned "with Mike" request shouldn't come back from
                # the dead and hijack an unrelated later reply.
                assistant = TammyAssistant()
                response = await assistant.process_message(
                    "Tomorrow at 2pm", db, session_id=session_id
                )
                assert response["intent"] == "unknown"

                appointments = await AppointmentService.get_user_appointments(db, DEFAULT_USER_ID)
                assert len(appointments) == 0
        finally:
            await engine.dispose()
