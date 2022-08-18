import logging
import os

# Use the package we installed
from app.slack_command_handler import register_command_handler
from slack_bolt import App
from app.command_factory import CommandFactory

# Initializes your app with your bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

command = "/scheduler-local"
# slackTable = "slack-apps"

# dynamodb_client = boto3.client(
#     'dynamodb',
#     aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
#     aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY")
# )


# @dataclass
# class Schedule:
#     app_pKey: "conversions_oncall-rotation"
#     sortKey: "schedule_current"
#     rota: list
#     start_dt: str


# @dataclass
# class User:
#     app_pKey: "conversions_oncall-rotation"
#     sortKey: str
#     History: dict


# dynamodb_resource = boto3.resource(
#     'dynamodb',
#     aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID_brainbug"),
#     aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY_brainbug")
# )
# dynamodb_resource: DynamoDb = DynamoDb()
logging.basicConfig(level=logging.INFO)


def dynamo_scan(logger):
    logger.info("Scanning table")
    # response = dynamodb_resource.Table(slackTable).query(
    #     KeyConditionExpression=Key('app_pKey').eq('app_slacker_chooser') & Key('sortKey').eq('user_U03RHF27HRP')
    # )
    # response = dynamodb_resource.get_schedule()
    # logger.info(response)
    # response = dynamodb_resource.Table('ISS_locations').scan()
    # for i in response['Items']:
    #     logger.info(i)
    # dynamodb_resource.Table('slack_apps').put_item(
    #     Item=asdict(Schedule("app_rota", "schedule", ["U03RHF27HRP"], date.today().strftime("%d/%m/%Y"))))


def respond_to_slack_within_3_seconds(body, ack, logger):
    logger.info(body)
    # user_id = re.search(r"<@(\w+)\|", body['text'])
    # logger.info(user_id.group())
    # logger.info(user_id.group(1))
    if body.get("text") is None:
        ack(f":x: Usage: {command} (description here)")
    else:
        title = body["text"]
        ack(f"Accepted! (task: {title})")
    # dynamo_scan(logger)


# @app.command(command)
def process_request(ack, respond, body, logger, client):
    respond_to_slack_within_3_seconds(body, ack, logger)
    # if 'user_id' in body:
    #     user_response = client.users_info(user=f"{body['user_name']}")
    #     logger.info("user received")
    #     logger.info(user_response)
    #     logger.info(f"{user_response['user']}")
    #     respond(f"<@{user_response['user']['id']}>")
    # elif 'text' in body:
    #     logger.info("command received")
    #     logger.info(body)
    #     title = body["text"]
    #     respond(f"Completed! (task: {title})")
    # else:
    #     logger.info("nothing interesting")
    #     respond("usage error")
    cmd_body: list = body["text"].split()
    subcommand = cmd_body[0]
    logger.info("subcommand is " + subcommand)

    # get args from subcommand
    #     ex: to extract userid re.search(r"<@(\w+)\|"
    try:
        CommandFactory.get_command(subcommand, logger).execute(logger, respond)
    except Exception as e:
        respond(str(e))
    # if subcommand is "next":
    #     subcommand_next()
    # elif subcommand is "swap":
    #     subcommand_swap()
    # elif subcommand is "show":
    #     subcommand_show()
    # elif subcommand is "history":
    #     subcommand_history()


# def validate_dynamo_db():
#     dynamodb_resource.Table(slackTable) is not None
#   what is returned when using this against a non-existent table???


# def validate_user(user: str):
#   call slack api to validate that user is a member of conversions team

# def subcommand_next():
#
# def subcommand_swap():
#
# def subcommand_show():
#
# def subcommand_history():


@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    try:
        # views.publish is the method that your app uses to push a view to the Home tab
        client.views_publish(
            # the user that opened your app's app home
            user_id=event["user"],
            # the view object that appears in the app home
            view={
                "type": "home",
                "callback_id": "home_view",

                # body of the view
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Welcome to your _App's Home_* :tada:"
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "This button won't do much for now but you can set up a listener for it using the `actions()` method and passing its unique `action_id`. See an example in the `examples` folder within your Bolt app."
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Click me!"
                                }
                            }
                        ]
                    }
                ]
            }
        )

    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")


# app.command(command)(ack=respond_to_slack_within_3_seconds, lazy=[process_request])

# Start your app
if __name__ == "__main__":
    register_command_handler(app, command)
    app.start(port=int(os.environ.get("PORT", 3000)))
