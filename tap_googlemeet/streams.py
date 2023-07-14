"""Stream type classes for tap-googlemeet."""

from __future__ import annotations

from pathlib import Path

from tap_googlemeet.client import GoogleMeetStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class CallEndedStream(GoogleMeetStream):
    """Define custom stream."""

    name = "call_ended"
    primary_keys = ["id"]
    replication_key = "start_date"
    schema_filepath = SCHEMAS_DIR / "call_ended.json"
