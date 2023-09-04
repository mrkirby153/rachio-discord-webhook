# Rachio Discord Webhook

An app to bridge between Rachio and Discord webhooks

## Setup

**Note:** This app uses webhooks so it must be reachable by the internet.

1. Get your Rachio API token by following the instructions [here](https://rachio.readme.io/reference/authentication).
2. Create a Discord webhook
3. Set `RACHIO_API_KEY` and `DISCORD_WEBHOOK_URL` environment variables
4. Retrieve your controller's device id by running `python manage.py get-devices`
5. Set `RACHIO_DEVICE_ID` to the controller you wish to monitor
6. Set a `RACHIO_WEBHOOK_SECRET_KEY` webhook secret to secure your webhook
7. Initialize the controller's webhook by running `python manage.py create-webhook`
8. Start the app

## Docker

If using the docker image, you may need to activate the virtual environment with `source /venv/bin/activate` before running `python manage.py`
