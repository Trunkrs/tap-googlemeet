"""GoogleMeet tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_googlemeet import streams


class TapGoogleMeet(Tap):
    """GoogleMeet tap class."""

    name = "tap-googlemeet"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "credentials_file",
            th.StringType,
            required=True,
            description="Link to the credentials file",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            required=True
        )
    ).to_dict()

    def discover_streams(self) -> list[streams.GoogleMeetStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.CallEndedStream(self),
        ]


if __name__ == "__main__":
    TapGoogleMeet.cli()
