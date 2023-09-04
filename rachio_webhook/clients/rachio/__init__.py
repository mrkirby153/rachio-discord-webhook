import json
from typing import Any, Literal, Optional

import requests
from decouple import config

from rachio_webhook.clients.rachio.event_types import EventTypes

HttpMethod = Literal["get", "post", "put", "patch", "delete"]

WEBHOOK_SUBSCRIBED_TYPES = [
    EventTypes.DEVICE_STATUS_EVENT,
    EventTypes.SCHEDULE_STATUS_EVENT,
    EventTypes.ZONE_STATUS_EVENT,
]


class RachioClient:
    _INSTANCE: Optional["RachioClient"] = None

    @classmethod
    def instance(cls) -> "RachioClient":
        if cls._INSTANCE is None:
            cls._INSTANCE = cls()
        return cls._INSTANCE

    @classmethod
    def public_webhook_url(cls) -> str:
        return f"{config('PUBLIC_URL')}/webhook/{config('RACHIO_WEBHOOK_SECRET_KEY')}"

    def __init__(self):
        self._api_key = config("RACHIO_API_KEY")

    def get_person(self) -> dict:
        person_id = self._make_request("get", "/person/info", raise_for_status=True)[
            "id"
        ]
        return self._make_request("get", f"/person/{person_id}", raise_for_status=True)

    def get_devices(self) -> dict:
        person = self.get_person()
        return person["devices"]

    def get_device(self, device_id: str) -> dict:
        devices = self.get_devices()
        return next(filter(lambda device: device["id"] == device_id, devices), None)

    def get_webhooks_for_device(self, device_id: str) -> list:
        return self._make_request(
            "get", f"/notification/{device_id}/webhook", raise_for_status=True
        )

    def create_webhook_for_device(
        self, device_id: str, url: str, event_types: list[EventTypes], external_id: str
    ) -> Any:
        event_types = [{"id": event_type.value} for event_type in event_types]
        return self._make_request(
            "post",
            "/notification/webhook",
            raise_for_status=True,
            body={
                "device": {"id": device_id},
                "externalId": external_id,
                "url": url,
                "eventTypes": event_types,
            },
        )

    def update_webhook_for_device(
        self, webhook_id: str, url: str, event_types: list[EventTypes], external_id: str
    ) -> Any:
        event_types = [{"id": event_type.value} for event_type in event_types]
        return self._make_request(
            "put",
            "/notification/webhook",
            raise_for_status=True,
            body={
                "id": webhook_id,
                "externalId": external_id,
                "url": url,
                "eventTypes": event_types,
            },
        )

    def _make_request(
        self,
        method: HttpMethod,
        url: str,
        body: Optional[Any] = None,
        raise_for_status: Optional[bool] = False,
    ) -> Any:
        url = f"https://api.rach.io/1/public{url}"
        method = getattr(requests, method.lower())
        resp = method(
            url,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            data=json.dumps(body),
        )
        if raise_for_status:
            resp.raise_for_status()
        return resp.json()


def create_or_update_webhook(device_id: str):
    client = RachioClient.instance()
    webhooks = client.get_webhooks_for_device(device_id)
    found_webhook = next(
        filter(lambda webhook: webhook["externalId"] == "rachio_webhook", webhooks),
        None,
    )
    if found_webhook:
        print("Found webhook, updating...")
        client.update_webhook_for_device(
            found_webhook["id"],
            RachioClient.public_webhook_url(),
            WEBHOOK_SUBSCRIBED_TYPES,
            "rachio_webhook",
        )
    else:
        print("Webhook not found, creating...")
        client.create_webhook_for_device(
            device_id,
            RachioClient.public_webhook_url(),
            WEBHOOK_SUBSCRIBED_TYPES,
            "rachio_webhook",
        )
