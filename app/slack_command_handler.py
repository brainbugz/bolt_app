import logging
import re

from . import dynamo_db
from .command_factory import CommandFactory
from .exceptions import UsageException
from slack_bolt import App

command = "/scheduler-next"
subcommands = ["swap", "history", "next", "add", "remove", "show"]


def register_command_handler(app: App, slack_command: str):
    app.command(slack_command)(process_request)
    global command
    command = slack_command


def respond_to_slack_within_3_seconds(body, ack, logger):
    logger.info(body)
    if body.get("text") is None:
        ack(f":x: Usage: {command} - {subcommands}")
    else:
        title = body["text"]
        ack(f"Processing task: {title}")


def process_request(ack, respond, body, logger, client):
    if not is_valid_user(body):
        ack("Not authorized.")
        return

    respond_to_slack_within_3_seconds(body, ack, logger)
    if body.get('text') is None:
        return

    cmd_args: list = body["text"].split()
    if len(cmd_args) > 3:
        respond("Too many arguments.")
        return

    subcommand = cmd_args[0]
    user_args = re.findall(r"<@(\w+)\|", body['text'])

    try:
        CommandFactory.get_command(subcommand, user_args).execute(respond, client)
    except UsageException as ue:
        respond(str(ue))
    except Exception as e:
        logging.info(str(e))
        respond(str("Unknown error encountered"))


def is_valid_user(body):
    user_id = body['user_id']
    return user_id in dynamo_db.DynamoDb().get_schedule()['rotation']
