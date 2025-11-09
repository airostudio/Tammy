"""Tests for chat/AI functionality"""

import pytest
from app.ai.intent_parser import IntentParser
from app.ai.assistant import TammyAssistant


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
        assistant = TammyAssistant()
        response = await assistant.process_message("What appointments do I have today?")

        assert response["response"] is not None
        assert response["intent"] is not None
        assert isinstance(response["confidence"], float)

    async def test_conversation_history(self):
        """Test conversation history tracking"""
        assistant = TammyAssistant()
        await assistant.process_message("Hello")

        history = assistant.get_history()
        assert len(history) == 2  # User + Assistant

        assistant.clear_history()
        assert len(assistant.get_history()) == 0
