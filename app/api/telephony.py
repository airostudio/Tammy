"""Carrier-agnostic telephony webhook receiver.

Each supported carrier gets its own webhook URL
(/api/telephony/webhook/{provider_name}) to configure in that carrier's
dashboard, but they all share the same signature verification -> event
parsing -> call handling pipeline. Adding a new carrier means adding an
adapter in app.telephony.providers and registering it in
app.telephony.registry - this router and the call handling logic never
change.
"""

from fastapi import APIRouter, HTTPException, Request

from app.config import get_settings
from app.telephony.call_handler import CallEventHandler
from app.telephony.registry import get_telephony_provider

router = APIRouter()
call_handler = CallEventHandler()


@router.post("/webhook/{provider_name}")
async def telephony_webhook(provider_name: str, request: Request):
    """Single entry point for every supported carrier's inbound webhooks."""
    try:
        provider = get_telephony_provider(provider_name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    raw_body = await request.body()
    headers = dict(request.headers)

    settings = get_settings()
    base_url = (settings.public_base_url or str(request.base_url)).rstrip("/")
    full_url = f"{base_url}{request.url.path}"
    if request.url.query:
        full_url = f"{full_url}?{request.url.query}"

    if not provider.verify_signature(headers, raw_body, full_url):
        raise HTTPException(status_code=403, detail="Invalid webhook signature")

    event = provider.parse_event(headers, raw_body)
    actions = await call_handler.handle_event(event)
    response = await provider.execute_actions(event, actions)

    if response is not None:
        return response
    return {"status": "received"}
