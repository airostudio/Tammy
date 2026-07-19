"""Carrier-agnostic telephony abstraction.

Business logic (deciding what should happen next on a call) is written
once against the types in `app.telephony.models` and never touches a
provider SDK directly. Each carrier gets an adapter in
`app.telephony.providers` that implements `TelephonyProvider` and
translates to/from that carrier's webhook and call-control format.
"""
