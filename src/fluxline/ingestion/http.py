from dataclasses import dataclass
from datetime import datetime

"""
============================================================================================================
HTTP response snapshot dataclass
============================================================================================================

I am wanting the HTTP response to become an explict object (immutable).

This dataclass is used to store the HTTP response snapshot, including the URL, status code, headers, 
and body. It is designed to be immutable and uses slots for memory efficiency. This is fine since I am 
constructing it from a known HTTP response and I don't need to modify it after creation.

This is part of a refactor. Prior to this ElexonClient.fetch_fuelhh() goes directly from HTTP to 
pydantic model validation. So the refactor captures the HTTP response in an explicit object first.

============================================================================================================
"""

@dataclass(frozen=True, slots=True)
class HttpResponseSnapshot:
    url: str
    status_code: int
    received_at: datetime
    headers: dict[str, str]
    body: bytes
