import json

from decouple import config
from flask import Flask, request

from rachio_webhook.clients.rachio import RachioClient
from rachio_webhook.event_handlers.rachio import IncomingMessages

app = Flask(__name__)
rachio_client = RachioClient.instance()


@app.route("/")
def main():
    return f"OK"


@app.route("/webhook/<secret>", methods=["POST"])
def webhook(secret: str):
    if secret != config("RACHIO_WEBHOOK_SECRET_KEY"):
        return "Unauthorized", 401
    body = json.loads(request.data)
    IncomingMessages.instance().handle_incoming_message(body)
    return "OK"
