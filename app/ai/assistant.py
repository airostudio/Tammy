"""Tammy AI Assistant - Main conversation handler.

Turns a parsed intent into a real action against the database (create
an appointment, save a contact, ...) rather than just describing what
it would do. The intent parsing itself is still regex-based
(app/ai/intent_parser.py) - upgrading that to a real LLM is a
separate, larger piece of work (OPENAI_API_KEY is already configured
but unused).
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.intent_parser import IntentParser
from app.schemas.appointment import AppointmentCreate
from app.schemas.contact import ContactCreate
from app.schemas.message import MessageCreate
from app.schemas.task import TaskCreate
from app.schemas.visitor import VisitorCreate
from app.services.appointment_service import AppointmentService
from app.services.contact_service import ContactService
from app.services.message_service import MessageService
from app.services.task_service import TaskService
from app.services.visitor_service import VisitorService
from app.utils.default_user import DEFAULT_USER_ID, ensure_default_user

logger = logging.getLogger(__name__)

_TASK_TITLE_PREFIXES = [
    r"^remind me to\s+",
    r"^i need to\s+",
    r"^don't forget to\s+",
    r"^(?:create|add|new)\s+(?:a\s+)?task\s+(?:to\s+)?",
]


class TammyAssistant:
    """Main AI assistant class for Tammy"""

    def __init__(self):
        self.intent_parser = IntentParser()
        self.conversation_history: List[Dict[str, str]] = []

    async def process_message(
        self, message: str, db: AsyncSession, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a user message, take any real action it implies, and reply"""
        parsed = self.intent_parser.parse(message)

        self.conversation_history.append({"role": "user", "content": message})

        try:
            response = await self._generate_response(parsed, context or {}, db)
        except Exception:
            logger.exception("Failed to handle intent '%s'", parsed.get("intent"))
            response = {
                "response": "Sorry, I ran into a problem doing that. Could you try again?",
                "intent": parsed.get("intent"),
                "entities": parsed.get("entities", {}),
                "actions": [],
                "confidence": 0.0,
                "suggestions": [],
            }

        self.conversation_history.append({"role": "assistant", "content": response["response"]})

        return response

    async def _generate_response(
        self, parsed: Dict[str, Any], context: Dict[str, Any], db: AsyncSession
    ) -> Dict[str, Any]:
        """Dispatch to the handler for the parsed intent"""
        intent = parsed["intent"]
        entities = parsed["entities"]
        original_message = parsed["original_message"]

        handlers = {
            "schedule_appointment": self._handle_schedule_appointment,
            "check_calendar": self._handle_check_calendar,
            "create_task": self._handle_create_task,
            "check_tasks": self._handle_check_tasks,
            "add_contact": self._handle_add_contact,
            "find_contact": self._handle_find_contact,
            "check_in_visitor": self._handle_check_in_visitor,
            "check_messages": self._handle_check_messages,
            "draft_email": self._handle_draft_email,
        }

        handler = handlers.get(intent)
        if handler is None:
            return await self._handle_unknown(parsed)
        return await handler(entities, db, original_message)

    async def _handle_schedule_appointment(
        self, entities: Dict[str, Any], db: AsyncSession, original_message: str
    ) -> Dict[str, Any]:
        """Create a real appointment once we have a date and time"""
        if "date" not in entities or "time" not in entities:
            missing = [part for part, key in (("a date", "date"), ("a time", "time")) if key not in entities]
            response = "I'd be glad to schedule that. "
            if entities.get("names"):
                response += f"With {', '.join(entities['names'])}. "
            response += f"What {' and '.join(missing)} works for you?"
            return {
                "response": response,
                "intent": "schedule_appointment",
                "entities": entities,
                "actions": [],
                "confidence": 0.6,
                "suggestions": ["Tomorrow at 2pm", "Next Monday at 10am", "Cancel"],
            }

        await ensure_default_user(db)

        date_str = entities["date"].strftime("%Y-%m-%d")
        start_time = datetime.strptime(f"{date_str} {entities['time']}", "%Y-%m-%d %H:%M")
        duration_minutes = entities.get("duration_minutes", 60)
        names = entities.get("names", [])
        title = f"Meeting with {', '.join(names)}" if names else "Meeting"

        appointment = await AppointmentService.create_appointment(
            db,
            AppointmentCreate(
                user_id=DEFAULT_USER_ID,
                title=title,
                start_time=start_time,
                duration_minutes=duration_minutes,
                attendees=names,
            ),
        )

        response = (
            f'Done - I\'ve booked "{title}" for {start_time.strftime("%A, %B %d at %I:%M %p")} '
            f"({duration_minutes} minutes)."
        )

        return {
            "response": response,
            "intent": "schedule_appointment",
            "entities": entities,
            "actions": [{"type": "appointment_created", "data": {"id": appointment.id}}],
            "confidence": 0.9,
            "suggestions": ["Check my calendar", "Schedule another", "Reschedule"],
        }

    async def _handle_check_calendar(
        self, entities: Dict[str, Any], db: AsyncSession, original_message: str
    ) -> Dict[str, Any]:
        """List real appointments for the requested day, or the week ahead"""
        if "date" in entities:
            start = datetime.combine(entities["date"], datetime.min.time())
            end = start + timedelta(days=1)
            period_label = start.strftime("%A, %B %d")
        else:
            start = datetime.utcnow()
            end = start + timedelta(days=7)
            period_label = "the next 7 days"

        appointments = await AppointmentService.get_user_appointments(db, DEFAULT_USER_ID, start, end)

        if not appointments:
            response = f"You have no appointments for {period_label}."
        else:
            lines = [
                f"- {a.title} at {a.start_time.strftime('%I:%M %p')} ({a.duration_minutes} min)"
                for a in appointments
            ]
            response = f"Here's what's on your calendar for {period_label}:\n" + "\n".join(lines)

        return {
            "response": response,
            "intent": "check_calendar",
            "entities": entities,
            "actions": [{"type": "appointments_listed", "data": {"count": len(appointments)}}],
            "confidence": 0.9,
            "suggestions": ["Schedule a meeting", "Show tomorrow", "Show this week"],
        }

    async def _handle_create_task(
        self, entities: Dict[str, Any], db: AsyncSession, original_message: str
    ) -> Dict[str, Any]:
        """Create a real task"""
        await ensure_default_user(db)

        title = self._extract_task_title(original_message)

        due_date = None
        if "date" in entities:
            due_date = datetime.combine(entities["date"], datetime.min.time())
            if "time" in entities:
                hour, minute = (int(part) for part in entities["time"].split(":"))
                due_date = due_date.replace(hour=hour, minute=minute)

        task = await TaskService.create_task(
            db,
            TaskCreate(
                user_id=DEFAULT_USER_ID,
                title=title,
                due_date=due_date,
                priority=entities.get("priority", "medium"),
            ),
        )

        response = f'Done - I\'ve added "{title}" to your task list'
        if due_date:
            response += f", due {due_date.strftime('%B %d, %Y')}"
        response += "."

        return {
            "response": response,
            "intent": "create_task",
            "entities": entities,
            "actions": [{"type": "task_created", "data": {"id": task.id}}],
            "confidence": 0.9,
            "suggestions": ["Show my tasks", "Mark as complete", "Set another reminder"],
        }

    @staticmethod
    def _extract_task_title(message: str) -> str:
        """Strip common trigger phrases and trailing date clauses to get a clean title"""
        title = message.strip()
        for pattern in _TASK_TITLE_PREFIXES:
            title = re.sub(pattern, "", title, flags=re.IGNORECASE)
        title = re.sub(r"\s+(?:on|by|at)\s+\w.*$", "", title, flags=re.IGNORECASE).strip()
        if not title:
            return "New task"
        return title[0].upper() + title[1:]

    async def _handle_check_tasks(
        self, entities: Dict[str, Any], db: AsyncSession, original_message: str
    ) -> Dict[str, Any]:
        """List real pending tasks"""
        tasks = await TaskService.get_user_tasks(db, DEFAULT_USER_ID, status="pending")

        if not tasks:
            response = "You have no pending tasks."
        else:
            lines = []
            for t in tasks:
                line = f"- {t.title} ({t.priority} priority)"
                if t.due_date:
                    line += f", due {t.due_date.strftime('%b %d')}"
                lines.append(line)
            response = "Here are your pending tasks:\n" + "\n".join(lines)

        return {
            "response": response,
            "intent": "check_tasks",
            "entities": entities,
            "actions": [{"type": "tasks_listed", "data": {"count": len(tasks)}}],
            "confidence": 0.9,
            "suggestions": ["Show completed", "Show overdue", "Create new task"],
        }

    async def _handle_add_contact(
        self, entities: Dict[str, Any], db: AsyncSession, original_message: str
    ) -> Dict[str, Any]:
        """Save a real contact"""
        names = entities.get("names", [])
        if not names:
            return {
                "response": "Sure - what's their name?",
                "intent": "add_contact",
                "entities": entities,
                "actions": [],
                "confidence": 0.5,
                "suggestions": [],
            }

        await ensure_default_user(db)

        name_parts = names[0].split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        emails = entities.get("emails", [])
        phones = entities.get("phone_numbers", [])

        contact = await ContactService.create_contact(
            db,
            ContactCreate(
                user_id=DEFAULT_USER_ID,
                first_name=first_name,
                last_name=last_name,
                email=emails[0] if emails else None,
                phone_number=phones[0] if phones else None,
            ),
        )

        response = f"Saved {contact.full_name} to your contacts."
        if not (emails or phones):
            response += " Want to add their email or phone number?"

        return {
            "response": response,
            "intent": "add_contact",
            "entities": entities,
            "actions": [{"type": "contact_created", "data": {"id": contact.id}}],
            "confidence": 0.85,
            "suggestions": ["View contacts", "Add more details"],
        }

    async def _handle_find_contact(
        self, entities: Dict[str, Any], db: AsyncSession, original_message: str
    ) -> Dict[str, Any]:
        """Search real contacts"""
        names = entities.get("names", [])
        query = names[0] if names else ""

        if not query:
            return {
                "response": "Who would you like me to look up?",
                "intent": "find_contact",
                "entities": entities,
                "actions": [],
                "confidence": 0.5,
                "suggestions": [],
            }

        results = await ContactService.search_contacts(db, DEFAULT_USER_ID, query)

        if not results:
            response = f'I couldn\'t find anyone matching "{query}".'
        else:
            lines = []
            for c in results:
                line = f"- {c.full_name}"
                if c.company:
                    line += f", {c.company}"
                if c.email:
                    line += f" - {c.email}"
                lines.append(line)
            plural = "es" if len(results) != 1 else ""
            response = f'Found {len(results)} match{plural} for "{query}":\n' + "\n".join(lines)

        return {
            "response": response,
            "intent": "find_contact",
            "entities": entities,
            "actions": [{"type": "contacts_found", "data": {"count": len(results)}}],
            "confidence": 0.85,
            "suggestions": ["Show all contacts", "Add new contact"],
        }

    async def _handle_check_in_visitor(
        self, entities: Dict[str, Any], db: AsyncSession, original_message: str
    ) -> Dict[str, Any]:
        """Create and check in a real visitor record"""
        names = entities.get("names", [])
        if not names:
            return {
                "response": "Sure - what's the visitor's name?",
                "intent": "check_in_visitor",
                "entities": entities,
                "actions": [],
                "confidence": 0.5,
                "suggestions": [],
            }

        host_name = names[1] if len(names) > 1 else "Front desk"
        visitor = await VisitorService.create_visitor(
            db, VisitorCreate(full_name=names[0], host_name=host_name)
        )
        visitor = await VisitorService.check_in_visitor(db, visitor.id)

        response = f"Checked in {visitor.full_name}."

        return {
            "response": response,
            "intent": "check_in_visitor",
            "entities": entities,
            "actions": [{"type": "visitor_checked_in", "data": {"id": visitor.id}}],
            "confidence": 0.85,
            "suggestions": ["Show current visitors", "Check in another visitor"],
        }

    async def _handle_check_messages(
        self, entities: Dict[str, Any], db: AsyncSession, original_message: str
    ) -> Dict[str, Any]:
        """List real unread messages"""
        messages = await MessageService.get_unread_messages(db)

        if not messages:
            response = "You have no unread messages."
        else:
            lines = []
            for m in messages:
                sender = m.from_name or m.from_email or m.from_phone or "Unknown"
                subject = m.subject or m.snippet or "(no subject)"
                lines.append(f"- {m.message_type}: {sender} - {subject}")
            plural = "s" if len(messages) != 1 else ""
            response = f"You have {len(messages)} unread message{plural}:\n" + "\n".join(lines)

        return {
            "response": response,
            "intent": "check_messages",
            "entities": entities,
            "actions": [{"type": "messages_listed", "data": {"count": len(messages)}}],
            "confidence": 0.9,
            "suggestions": ["Show all messages", "Mark as read", "Archive"],
        }

    async def _handle_draft_email(
        self, entities: Dict[str, Any], db: AsyncSession, original_message: str
    ) -> Dict[str, Any]:
        """Save a real draft message (no SMTP sending is wired up yet)"""
        emails = entities.get("emails", [])
        if not emails:
            return {
                "response": "Who should I send it to?",
                "intent": "draft_email",
                "entities": entities,
                "actions": [],
                "confidence": 0.5,
                "suggestions": [],
            }

        message = await MessageService.create_message(
            db,
            MessageCreate(
                message_type="email",
                direction="outbound",
                to_email=emails[0],
                subject="(draft)",
                body=original_message,
            ),
        )

        response = f"I've saved a draft to {emails[0]}. Tell me what it should say and I'll update it."

        return {
            "response": response,
            "intent": "draft_email",
            "entities": entities,
            "actions": [{"type": "draft_saved", "data": {"id": message.id}}],
            "confidence": 0.75,
            "suggestions": ["Send", "Edit draft", "Cancel"],
        }

    async def _handle_unknown(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unknown or unclear requests"""
        return {
            "response": "I'm not sure I understand. I can help you with:\n"
            "- Scheduling appointments and meetings\n"
            "- Managing your tasks\n"
            "- Finding and adding contacts\n"
            "- Checking in visitors\n"
            "- Managing messages and emails\n"
            "What would you like me to help with?",
            "intent": "unknown",
            "entities": {},
            "actions": [],
            "confidence": 0.0,
            "suggestions": [
                "Schedule a meeting",
                "Show my tasks",
                "Check my calendar",
                "Find a contact",
            ],
        }

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.conversation_history
