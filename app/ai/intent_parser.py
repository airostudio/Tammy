"""Intent parser for understanding user requests"""

from typing import Dict, Any, Optional, List
import re
from datetime import datetime, timedelta
import json


class IntentParser:
    """Parse user intent from natural language"""

    # Intent patterns
    INTENT_PATTERNS = {
        "schedule_appointment": [
            r"schedule.*(?:meeting|appointment)",
            r"book.*(?:meeting|appointment)",
            r"set up.*(?:meeting|appointment)",
            r"arrange.*(?:meeting|appointment)",
        ],
        "check_calendar": [
            r"what.*(?:appointments?|meetings?|schedule)",
            r"show.*(?:appointments?|meetings?|calendar)",
            r"when.*(?:next|free|available)",
            r"(?:am i|what's) free",
        ],
        "create_task": [
            r"(?:create|add|new).*task",
            r"remind me to",
            r"i need to",
            r"don't forget to",
        ],
        "check_tasks": [
            r"what.*tasks?",
            r"show.*(?:tasks?|to-?do)",
            r"what.*need to do",
            r"what's.*due",
        ],
        "add_contact": [
            r"(?:add|create|new).*contact",
            r"save.*(?:contact|number|email)",
        ],
        "find_contact": [
            r"(?:find|search|look up).*contact",
            r"who is",
            r"contact.*(?:for|info)",
            r"(?:phone|email).*(?:for|of)",
        ],
        "check_in_visitor": [
            r"check in.*visitor",
            r"visitor.*(?:arrived|here)",
            r"(?:register|log).*visitor",
        ],
        "check_messages": [
            r"(?:any|check).*(?:messages?|emails?)",
            r"show.*(?:inbox|messages?|emails?)",
            r"what.*(?:new|unread)",
        ],
        "draft_email": [
            r"(?:draft|write|compose).*(?:email|message)",
            r"reply to",
            r"send.*(?:email|message)",
        ],
    }

    # Time extraction patterns
    TIME_PATTERNS = {
        "today": r"\btoday\b",
        "tomorrow": r"\btomorrow\b",
        "next_week": r"next week",
        "monday": r"\bmonday\b",
        "tuesday": r"\btuesday\b",
        "wednesday": r"\bwednesday\b",
        "thursday": r"\bthursday\b",
        "friday": r"\bfriday\b",
        "saturday": r"\bsaturday\b",
        "sunday": r"\bsunday\b",
    }

    @staticmethod
    def parse(message: str) -> Dict[str, Any]:
        """Parse user message and extract intent and entities"""
        message_lower = message.lower()

        # Detect intent
        intent = IntentParser._detect_intent(message_lower)

        # Extract entities based on intent
        entities = IntentParser._extract_entities(message_lower, intent)

        # Calculate confidence (simple heuristic)
        confidence = IntentParser._calculate_confidence(message_lower, intent, entities)

        return {
            "intent": intent,
            "entities": entities,
            "confidence": confidence,
            "original_message": message,
        }

    @staticmethod
    def _detect_intent(message: str) -> Optional[str]:
        """Detect the primary intent from the message"""
        for intent, patterns in IntentParser.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    return intent
        return "unknown"

    @staticmethod
    def _extract_entities(message: str, intent: str) -> Dict[str, Any]:
        """Extract relevant entities from the message"""
        entities = {}

        # Extract time/date entities
        time_info = IntentParser._extract_time(message)
        if time_info:
            entities.update(time_info)

        # Extract names (simple pattern - words starting with capitals)
        names = re.findall(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b", message)
        if names:
            entities["names"] = names

        # Extract emails
        emails = re.findall(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", message)
        if emails:
            entities["emails"] = emails

        # Extract phone numbers
        phones = re.findall(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", message)
        if phones:
            entities["phone_numbers"] = phones

        # Extract duration (e.g., "30 minutes", "1 hour")
        duration_match = re.search(r"(\d+)\s*(hour|minute|hr|min)s?", message, re.IGNORECASE)
        if duration_match:
            duration = int(duration_match.group(1))
            unit = duration_match.group(2).lower()
            if unit in ["hour", "hr"]:
                entities["duration_minutes"] = duration * 60
            else:
                entities["duration_minutes"] = duration

        # Extract priority (high, low, urgent)
        priority_match = re.search(r"\b(high|low|urgent|normal)\s*priority\b", message, re.IGNORECASE)
        if priority_match:
            entities["priority"] = priority_match.group(1).lower()

        return entities

    @staticmethod
    def _extract_time(message: str) -> Optional[Dict[str, Any]]:
        """Extract time and date information from message"""
        now = datetime.now()
        time_info = {}

        # Check for relative dates
        if re.search(IntentParser.TIME_PATTERNS["today"], message):
            time_info["date"] = now.date()
        elif re.search(IntentParser.TIME_PATTERNS["tomorrow"], message):
            time_info["date"] = (now + timedelta(days=1)).date()
        elif re.search(IntentParser.TIME_PATTERNS["next_week"], message):
            time_info["date"] = (now + timedelta(weeks=1)).date()

        # Check for specific weekdays
        for day, pattern in IntentParser.TIME_PATTERNS.items():
            if day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                if re.search(pattern, message):
                    # Simple logic: find next occurrence of that weekday
                    days_ahead = {
                        "monday": 0,
                        "tuesday": 1,
                        "wednesday": 2,
                        "thursday": 3,
                        "friday": 4,
                        "saturday": 5,
                        "sunday": 6,
                    }
                    target_day = days_ahead[day]
                    current_day = now.weekday()
                    days_until = (target_day - current_day) % 7
                    if days_until == 0:
                        days_until = 7  # Next week if it's the same day
                    time_info["date"] = (now + timedelta(days=days_until)).date()

        # Extract specific time (e.g., "2pm", "14:00", "2:30")
        time_match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", message, re.IGNORECASE)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            meridiem = time_match.group(3).lower() if time_match.group(3) else None

            if meridiem == "pm" and hour < 12:
                hour += 12
            elif meridiem == "am" and hour == 12:
                hour = 0

            time_info["time"] = f"{hour:02d}:{minute:02d}"

        return time_info if time_info else None

    @staticmethod
    def _calculate_confidence(message: str, intent: str, entities: Dict[str, Any]) -> float:
        """Calculate confidence score for the parsed intent"""
        if intent == "unknown":
            return 0.0

        confidence = 0.5  # Base confidence

        # Increase confidence if we found entities
        if entities:
            confidence += 0.2

        # Increase confidence if we found time information for time-based intents
        if intent in ["schedule_appointment", "create_task"] and ("date" in entities or "time" in entities):
            confidence += 0.2

        # Increase confidence if we found names for contact-related intents
        if intent in ["find_contact", "add_contact"] and "names" in entities:
            confidence += 0.1

        return min(confidence, 1.0)  # Cap at 1.0
