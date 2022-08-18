import logging

from app.command_factory import CommandFactory
from app.slack_command_handler import register_command_handler
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

# process_before_response must be True when running on FaaS
app = App(process_before_response=True)
logging.basicConfig(level=logging.INFO)

# @app.middleware  # or app.use(log_request)
# def log_request(logger, body, next):
#     logger.debug(body)
#     return next()

command = "/scheduler-next"
register_command_handler(app, command)


def respond_to_slack_within_3_seconds(body, ack):
    if body.get("text") is None:
        ack(f":x: Usage: {command} (description here)")
    else:
        title = body["text"]
        ack(f"Accepted! (task: {title})")


# @app.command(command)
def process_request(ack, respond, body, logger, client):
    respond_to_slack_within_3_seconds(body, ack)
    logger.info(body)

    cmd_body: list = body["text"].split()
    subcommand = cmd_body[0]
    logger.info("subcommand is " + subcommand)
    CommandFactory.get_command(subcommand, logger).execute(logger, respond)
    # if 'user_id' in body:
    #     user_response = client.users_info(user=f"{body['user_id']}")
    #     logger.debug("user received")
    #     logger.debug(user_response)
    #     logger.debug(f"{user_response['user']}")
    #     respond(f"<@{user_response['user']['id']}>!")
    # elif 'text' in body:
    #     logger.debug("command received")
    #     logger.debug(body)
    #     title = body["text"]
    #     respond(f"Completed! (task: {title})")
    # else:
    #     logger.debug("nothing interesting")
    #     respond("usage error")


# app.command(command)(ack=respond_to_slack_within_3_seconds, lazy=[process_request])

SlackRequestHandler.clear_all_log_handlers()
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)


def handler(event, context):
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)
