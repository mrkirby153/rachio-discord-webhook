import json
from typing import Dict, Optional

import dateutil.parser
from pluralizer import Pluralizer

from rachio_webhook.clients.discord import DiscordClient
from rachio_webhook.clients.rachio import RachioClient

pluralizer = Pluralizer()


class MessageHandler:
    def __init__(self) -> None:
        self.discord_client = DiscordClient.instance()
        self.rachio_client = RachioClient.instance()

    def handle(self, data: dict):
        print("Handling Message: ", data)
        handler_method = data.get("subType").lower()
        handler = getattr(self, f"handle_{handler_method}", None)
        generic_handler = getattr(self, "handle_generic", None)
        if handler is None and generic_handler is None:
            print(f"Unknown handler method: {handler_method} for {self}")
        handler(data) if handler is not None else generic_handler(data)


class ZoneMessageHandler(MessageHandler):
    def handle_zone_started(self, data: dict):
        end_time = dateutil.parser.parse(data.get("endTime"))
        duration = data.get("durationInMinutes")
        message = f":green_circle: **Zone {data.get('zoneName')}** started for {data.get('durationInMinutes')} {pluralizer.pluralize('minute', duration)} (Ends <t:{int(end_time.timestamp())}:R>)"
        self.discord_client.send_message(message)

    def handle_zone_completed(self, data: dict):
        message = f":white_check_mark: **Zone {data.get('zoneName')}** completed. Ran for {data.get('durationInMinutes')} {pluralizer.pluralize('minute', data.get('durationInMinutes'))}"
        self.discord_client.send_message(message)

    def handle_generic(self, data: dict):
        message = f"Generic Zone Message: ```json\n{json.dumps(data)}```"
        self.discord_client.send_message(message)


class DeviceMessageHandler(MessageHandler):
    def handle_offline(self, data: dict):
        device = self.rachio_client.get_device(data.get("deviceId"))
        message = f":warning: **{device['name']}** is offline"
        self.discord_client.send_message(message)

    def handle_online(self, data: dict):
        device = self.rachio_client.get_device(data.get("deviceId"))
        message = f":green_circle: **{device['name']}** is online"
        self.discord_client.send_message(message)

    def handle_generic(self, data: dict):
        message = f"Generic Device Message: ```json\n{json.dumps(data)}```"
        self.discord_client.send_message(message)


class ScheduleMessageHandler(MessageHandler):
    def handle_generic(self, data: dict):
        message = f"Generic Schedule Message: ```json\n{json.dumps(data)}```"
        self.discord_client.send_message(message)

    def handle_schedule_started(self, data: dict):
        end_time = dateutil.parser.parse(data.get("endTime"))
        duration = data.get("durationInMinutes")
        message = f":green_circle: **Schedule {data.get('scheduleName')}** started for {data.get('durationInMinutes')} {pluralizer.pluralize('minute', duration)} (Ends <t:{int(end_time.timestamp())}:R>)"
        self.discord_client.send_message(message)

    def handle_schedule_completed(self, data: dict):
        message = f":white_check_mark: **Schedule {data.get('scheduleName')}** completed. Ran for {data.get('durationInMinutes')} {pluralizer.pluralize('minute', data.get('durationInMinutes'))}"
        self.discord_client.send_message(message)


class IncomingMessages:
    _INSTANCE: Optional["IncomingMessages"] = None

    _message_handlers: Dict[str, MessageHandler] = {
        "device_status": DeviceMessageHandler(),
        "zone_status": ZoneMessageHandler(),
        "schedule_status": ScheduleMessageHandler(),
    }

    @classmethod
    def instance(cls) -> "IncomingMessages":
        if cls._INSTANCE is None:
            cls._INSTANCE = cls()
        return cls._INSTANCE

    def __init__(self) -> None:
        self.discord_client = DiscordClient.instance()
        self.rachio_client = RachioClient.instance()

    def handle_incoming_message(self, data: dict):
        handler = self._message_handlers.get(data.get("type").lower())
        if handler is None:
            message = f"Unhandled Message: ```json\n{json.dumps(data)}```"
            self.discord_client.send_message(message)
            return
        handler.handle(data)
