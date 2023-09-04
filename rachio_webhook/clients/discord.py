from typing import Any, Optional

import requests
from decouple import config


class DiscordClient:
    _INSTANCE: Optional["DiscordClient"] = None

    @classmethod
    def instance(cls) -> "DiscordClient":
        if cls._INSTANCE is None:
            cls._INSTANCE = cls()
        return cls._INSTANCE

    def __init__(self):
        self._webhook_url = config("DISCORD_WEBHOOK_URL")

    def post_webhook(self, body: Any):
        resp = requests.post(self._webhook_url, json=body)
        resp.raise_for_status()

    def send_message(self, body: str):
        return self.post_webhook({"content": body})
