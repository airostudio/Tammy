"""Example usage of ENDCOM.NET AI Assistant API"""

import asyncio
import httpx
from datetime import datetime, timedelta


BASE_URL = "http://localhost:8000/api"


async def example_chat():
    """Example: Chat with Tammy"""
    print("\n=== Chat Example ===")
    async with httpx.AsyncClient() as client:
        # Send a message to Tammy
        response = await client.post(
            f"{BASE_URL}/chat",
            json={"message": "Schedule a meeting with John tomorrow at 2pm"},
        )
        print(f"User: Schedule a meeting with John tomorrow at 2pm")
        print(f"Tammy: {response.json()['response']}")
        print(f"Intent: {response.json()['intent']}")
        print(f"Confidence: {response.json()['confidence']}")


async def example_appointments():
    """Example: Create and manage appointments"""
    print("\n=== Appointments Example ===")
    async with httpx.AsyncClient() as client:
        # Create an appointment
        tomorrow = datetime.now() + timedelta(days=1)
        appointment_data = {
            "user_id": "user123",
            "title": "Team Meeting",
            "description": "Weekly team sync",
            "start_time": tomorrow.replace(hour=14, minute=0).isoformat(),
            "duration_minutes": 60,
            "attendees": ["john@example.com", "sarah@example.com"],
            "location": "Conference Room A",
        }

        response = await client.post(f"{BASE_URL}/appointments", json=appointment_data)
        if response.status_code == 201:
            appointment = response.json()
            print(f"Created appointment: {appointment['title']}")
            print(f"Start time: {appointment['start_time']}")
            print(f"Attendees: {', '.join(appointment['attendees'])}")

            # Get appointments for user
            response = await client.get(f"{BASE_URL}/appointments?user_id=user123")
            appointments = response.json()
            print(f"\nTotal appointments: {len(appointments)}")


async def example_tasks():
    """Example: Create and manage tasks"""
    print("\n=== Tasks Example ===")
    async with httpx.AsyncClient() as client:
        # Create a task
        task_data = {
            "user_id": "user123",
            "title": "Review project proposal",
            "description": "Review and provide feedback on Q4 proposal",
            "priority": "high",
            "due_date": (datetime.now() + timedelta(days=3)).isoformat(),
            "project": "Q4 Planning",
        }

        response = await client.post(f"{BASE_URL}/tasks", json=task_data)
        if response.status_code == 201:
            task = response.json()
            print(f"Created task: {task['title']}")
            print(f"Priority: {task['priority']}")
            print(f"Due date: {task['due_date']}")

            # Get tasks for user
            response = await client.get(f"{BASE_URL}/tasks?user_id=user123")
            tasks = response.json()
            print(f"\nTotal tasks: {len(tasks)}")


async def example_contacts():
    """Example: Create and search contacts"""
    print("\n=== Contacts Example ===")
    async with httpx.AsyncClient() as client:
        # Create a contact
        contact_data = {
            "user_id": "user123",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone_number": "555-1234",
            "company": "Acme Corp",
            "job_title": "Product Manager",
            "tags": ["colleague", "product"],
        }

        response = await client.post(f"{BASE_URL}/contacts", json=contact_data)
        if response.status_code == 201:
            contact = response.json()
            print(f"Created contact: {contact['full_name']}")
            print(f"Email: {contact['email']}")
            print(f"Company: {contact['company']}")

            # Search contacts
            response = await client.get(f"{BASE_URL}/contacts/search/?user_id=user123&query=John")
            contacts = response.json()
            print(f"\nSearch results: {len(contacts)} contacts found")


async def example_visitors():
    """Example: Check in a visitor"""
    print("\n=== Visitors Example ===")
    async with httpx.AsyncClient() as client:
        # Create a visitor record
        visitor_data = {
            "full_name": "Jane Smith",
            "company": "Client Corp",
            "email": "jane@clientcorp.com",
            "host_name": "John Doe",
            "visit_type": "in_person",
            "purpose": "Product demo",
            "scheduled_time": datetime.now().isoformat(),
        }

        response = await client.post(f"{BASE_URL}/visitors", json=visitor_data)
        if response.status_code == 201:
            visitor = response.json()
            print(f"Registered visitor: {visitor['full_name']}")
            print(f"Visiting: {visitor['host_name']}")
            print(f"Purpose: {visitor['purpose']}")

            # Check in the visitor
            visitor_id = visitor["id"]
            response = await client.post(
                f"{BASE_URL}/visitors/{visitor_id}/check-in", params={"badge_number": "BADGE-001"}
            )
            if response.status_code == 200:
                checked_in = response.json()
                print(f"\nVisitor checked in at: {checked_in['check_in_time']}")
                print(f"Badge number: {checked_in['badge_number']}")


async def main():
    """Run all examples"""
    print("=" * 50)
    print("ENDCOM.NET AI Assistant - Example Usage")
    print("=" * 50)

    try:
        await example_chat()
        await example_appointments()
        await example_tasks()
        await example_contacts()
        await example_visitors()

        print("\n" + "=" * 50)
        print("All examples completed!")
        print("=" * 50)
    except httpx.ConnectError:
        print("\nError: Could not connect to ENDCOM.NET API.")
        print("Make sure the server is running: python -m uvicorn app.main:app --reload")


if __name__ == "__main__":
    asyncio.run(main())
