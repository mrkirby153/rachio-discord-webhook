from decouple import config
from flask.cli import FlaskGroup

from rachio_webhook.clients.rachio import (RachioClient,
                                           create_or_update_webhook)
from rachio_webhook.flask import app

cli = FlaskGroup(app)


@cli.command()
def create_webhook():
    device_id = config("RACHIO_DEVICE_ID")
    print(f"Creating webhook for device {device_id}")
    create_or_update_webhook(device_id)
    print("Created!")


@cli.command()
def get_devices():
    client = RachioClient.instance()
    devices = client.get_devices()
    for device in devices:
        print(f"{device['name']}: {device['id']}")


if __name__ == "__main__":
    cli()
