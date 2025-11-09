"""Tammy AI Assistant - Main conversation handler"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import os

from app.ai.intent_parser import IntentParser
from app.config import get_settings

settings = get_settings()


class TammyAssistant:
    """Main AI assistant class for Tammy"""

    def __init__(self):
        self.intent_parser = IntentParser()
        self.conversation_history: List[Dict[str, str]] = []

    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a user message and generate a response"""
        # Parse intent and entities
        parsed = self.intent_parser.parse(message)

        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": message})

        # Generate response based on intent
        response = await self._generate_response(parsed, context or {})

        # Add assistant response to history
        self.conversation_history.append({"role": "assistant", "content": response["response"]})

        return response

    async def _generate_response(self, parsed: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate appropriate response based on parsed intent"""
        intent = parsed["intent"]
        entities = parsed["entities"]
        confidence = parsed["confidence"]

        # Map intents to actions
        if intent == "schedule_appointment":
            return await self._handle_schedule_appointment(entities, context)
        elif intent == "check_calendar":
            return await self._handle_check_calendar(entities, context)
        elif intent == "create_task":
            return await self._handle_create_task(entities, context)
        elif intent == "check_tasks":
            return await self._handle_check_tasks(entities, context)
        elif intent == "add_contact":
            return await self._handle_add_contact(entities, context)
        elif intent == "find_contact":
            return await self._handle_find_contact(entities, context)
        elif intent == "check_in_visitor":
            return await self._handle_check_in_visitor(entities, context)
        elif intent == "check_messages":
            return await self._handle_check_messages(entities, context)
        elif intent == "draft_email":
            return await self._handle_draft_email(entities, context)
        else:
            return await self._handle_unknown(parsed)

    async def _handle_schedule_appointment(self, entities: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle appointment scheduling requests"""
        actions = []

        # Extract appointment details
        appointment_data = {}

        if "names" in entities and entities["names"]:
            appointment_data["attendees"] = entities["names"]

        if "date" in entities:
            if "time" in entities:
                # Combine date and time
                date_str = entities["date"].strftime("%Y-%m-%d")
                datetime_str = f"{date_str} {entities['time']}"
                appointment_data["start_time"] = datetime_str
            else:
                appointment_data["date"] = entities["date"].strftime("%Y-%m-%d")

        if "duration_minutes" in entities:
            appointment_data["duration_minutes"] = entities["duration_minutes"]

        actions.append({
            "type": "schedule_appointment",
            "data": appointment_data
        })

        response = "I'll help you schedule that appointment. "

        if "date" in entities:
            response += f"I've noted it for {entities['date'].strftime('%B %d, %Y')}. "
        if "time" in entities:
            response += f"at {entities['time']}. "
        if "names" in entities and entities["names"]:
            response += f"with {', '.join(entities['names'])}. "

        if not ("date" in entities or "time" in entities):
            response += "When would you like to schedule it?"

        return {
            "response": response,
            "intent": "schedule_appointment",
            "entities": entities,
            "actions": actions,
            "confidence": 0.8,
            "suggestions": ["Check my calendar", "Find available time", "Cancel"],
        }

    async def _handle_check_calendar(self, entities: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle calendar check requests"""
        actions = [{
            "type": "get_appointments",
            "data": {"period": entities.get("date", "today")}
        }]

        response = "Let me check your calendar. "

        if "date" in entities:
            if entities["date"] == datetime.now().date():
                response += "Here are your appointments for today."
            else:
                response += f"Here are your appointments for {entities['date'].strftime('%B %d, %Y')}."
        else:
            response += "Here are your upcoming appointments."

        return {
            "response": response,
            "intent": "check_calendar",
            "entities": entities,
            "actions": actions,
            "confidence": 0.9,
            "suggestions": ["Schedule a meeting", "Show tomorrow", "Show this week"],
        }

    async def _handle_create_task(self, entities: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task creation requests"""
        task_data = {}

        if "date" in entities:
            task_data["due_date"] = entities["date"].strftime("%Y-%m-%d")

        if "priority" in entities:
            task_data["priority"] = entities["priority"]

        actions = [{
            "type": "create_task",
            "data": task_data
        }]

        response = "I've created a task for you. "

        if "date" in entities:
            response += f"Due date set to {entities['date'].strftime('%B %d, %Y')}. "

        if "priority" in entities:
            response += f"Priority: {entities['priority']}. "

        return {
            "response": response,
            "intent": "create_task",
            "entities": entities,
            "actions": actions,
            "confidence": 0.8,
            "suggestions": ["Show my tasks", "Mark as complete", "Set reminder"],
        }

    async def _handle_check_tasks(self, entities: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task checking requests"""
        actions = [{
            "type": "get_tasks",
            "data": {"status": "pending"}
        }]

        response = "Here are your current tasks."

        return {
            "response": response,
            "intent": "check_tasks",
            "entities": entities,
            "actions": actions,
            "confidence": 0.9,
            "suggestions": ["Show completed", "Show overdue", "Create new task"],
        }

    async def _handle_add_contact(self, entities: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle contact addition requests"""
        contact_data = {}

        if "names" in entities and entities["names"]:
            contact_data["name"] = entities["names"][0]

        if "emails" in entities:
            contact_data["email"] = entities["emails"][0]

        if "phone_numbers" in entities:
            contact_data["phone"] = entities["phone_numbers"][0]

        actions = [{
            "type": "add_contact",
            "data": contact_data
        }]

        response = "I'll save this contact. "

        if "names" in entities:
            response += f"Name: {entities['names'][0]}. "

        if not ("emails" in entities or "phone_numbers" in entities):
            response += "Please provide their email or phone number."

        return {
            "response": response,
            "intent": "add_contact",
            "entities": entities,
            "actions": actions,
            "confidence": 0.7,
            "suggestions": ["View contacts", "Add more details"],
        }

    async def _handle_find_contact(self, entities: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle contact search requests"""
        search_query = entities.get("names", [""])[0] if "names" in entities else ""

        actions = [{
            "type": "search_contacts",
            "data": {"query": search_query}
        }]

        response = f"Searching for contact: {search_query}" if search_query else "Please provide a name to search for."

        return {
            "response": response,
            "intent": "find_contact",
            "entities": entities,
            "actions": actions,
            "confidence": 0.8,
            "suggestions": ["Show all contacts", "Add new contact"],
        }

    async def _handle_check_in_visitor(self, entities: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle visitor check-in requests"""
        visitor_data = {}

        if "names" in entities and entities["names"]:
            visitor_data["name"] = entities["names"][0]

        actions = [{
            "type": "check_in_visitor",
            "data": visitor_data
        }]

        response = "I'll check in the visitor. "

        if "names" in entities:
            response += f"Visitor name: {entities['names'][0]}. "
        else:
            response += "What's the visitor's name?"

        return {
            "response": response,
            "intent": "check_in_visitor",
            "entities": entities,
            "actions": actions,
            "confidence": 0.7,
            "suggestions": ["Show current visitors", "Schedule visitor"],
        }

    async def _handle_check_messages(self, entities: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle message checking requests"""
        actions = [{
            "type": "get_messages",
            "data": {"status": "unread"}
        }]

        response = "Checking your messages..."

        return {
            "response": response,
            "intent": "check_messages",
            "entities": entities,
            "actions": actions,
            "confidence": 0.9,
            "suggestions": ["Show all messages", "Mark as read", "Archive"],
        }

    async def _handle_draft_email(self, entities: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle email drafting requests"""
        email_data = {}

        if "emails" in entities:
            email_data["to"] = entities["emails"][0]

        actions = [{
            "type": "draft_email",
            "data": email_data
        }]

        response = "I'll help you draft an email. "

        if "emails" in entities:
            response += f"To: {entities['emails'][0]}. "
        else:
            response += "Who should I send it to?"

        return {
            "response": response,
            "intent": "draft_email",
            "entities": entities,
            "actions": actions,
            "confidence": 0.7,
            "suggestions": ["Send", "Save as draft", "Cancel"],
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
