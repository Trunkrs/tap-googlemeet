"""REST client handling, including GoogleMeetStream base class."""
from __future__ import annotations

import os
from typing import Callable

import requests
from iso8601 import iso8601
from singer_sdk import Tap
from singer_sdk.streams import Stream

import logging

from tap_googlemeet.secrets_manager import get_secret, update_secret

_Auth = Callable[[requests.PreparedRequest], requests.PreparedRequest]

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/admin.reports.audit.readonly']

def get_external_credentials(config, sectret_id):
    if not config:
        config = get_secret(sectret_id)
    return config
def get_credentials(config, sectret_id):
    creds = Credentials.from_authorized_user_info(config, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(config, scopes=SCOPES)
            creds = flow.run_local_server(port=0)
        update_secret(config, sectret_id)
    return creds

class GoogleMeetStream(Stream):
    """GoogleMeet stream class."""
    _credentials = None

    def get_records(self, context: dict | None):
        replication_key = self.get_starting_replication_key_value(context)

        self._credentials = get_external_credentials(self._credentials, self.config.get('secret_id'))
        creds = get_credentials(self._credentials, self.config.get('secret_id'))

        service = build('admin', 'reports_v1', credentials=creds)

        nextPageToken = None

        while True:
            response = service.activities().list(userKey='all',applicationName='meet',eventName=self.name, startTime=replication_key, pageToken=nextPageToken).execute()
            nextPageToken = response.get('nextPageToken', None)
            activities = response.get('items', [])

            for activity in activities:
                yield self.post_process(activity)

            logging.info(f"Loaded {len(activities)} activities")

            if nextPageToken is None:
                break

    def post_process(
        self,
        row: dict,
        context: dict | None = None,  # noqa: ARG002
    ) -> dict | None:
        """Post-process a record after it is fetched."""
        result = {}
        result['id'] = row['id']['uniqueQualifier']
        result['start_date'] = iso8601.parse_date(row['id']['time'])
        if 'actor' in row:
            if 'email' in row['actor']:
                result['actor_email'] = row['actor']['email']
            if 'profileId' in row['actor']:
                result['actor_profile_id'] = row['actor']['profileId']
            if 'callerType' in row['actor']:
                result['actor_caller_type'] = row['actor']['callerType']
        result['etag'] = row['etag']

        if 'events' in row and len(row['events']) > 0:
            for parameter in row['events'][0]['parameters']:
                value_key = next(filter(lambda key: key != 'name',parameter.keys()), None)
                result[f"event_{parameter['name']}"] = parameter[value_key]

        return result

