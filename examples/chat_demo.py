"""Interactive chat demo with Tammy"""

import asyncio
import httpx


async def chat_with_tammy():
    """Interactive chat session with Tammy"""
    print("=" * 60)
    print("Welcome to Tammy AI Assistant - Interactive Chat Demo")
    print("=" * 60)
    print("\nType 'quit' or 'exit' to end the conversation")
    print("Type 'help' to see what Tammy can do\n")

    base_url = "http://localhost:8000/api/chat"

    async with httpx.AsyncClient() as client:
        while True:
            try:
                # Get user input
                user_input = input("\nYou: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["quit", "exit", "bye"]:
                    print("\nTammy: Goodbye! Have a great day!")
                    break

                # Send message to Tammy
                response = await client.post(base_url, json={"message": user_input})

                if response.status_code == 200:
                    data = response.json()
                    print(f"\nTammy: {data['response']}")

                    # Show intent and confidence
                    if data.get("intent") and data.get("intent") != "unknown":
                        print(f"  [Intent: {data['intent']} | Confidence: {data['confidence']:.2f}]")

                    # Show suggestions
                    if data.get("suggestions"):
                        print("\n  Suggestions:")
                        for i, suggestion in enumerate(data["suggestions"], 1):
                            print(f"    {i}. {suggestion}")
                else:
                    print(f"\nError: {response.status_code} - {response.text}")

            except httpx.ConnectError:
                print("\nError: Could not connect to Tammy.")
                print("Make sure the server is running: python -m uvicorn app.main:app --reload")
                break
            except KeyboardInterrupt:
                print("\n\nTammy: Goodbye! Have a great day!")
                break
            except Exception as e:
                print(f"\nError: {str(e)}")


if __name__ == "__main__":
    asyncio.run(chat_with_tammy())
