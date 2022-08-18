import logging
import os
from dataclasses import asdict
from datetime import date

import app.models
import boto3
from .models import Schedule, User
from boto3.dynamodb.conditions import Key


class DynamoDb:
    def __init__(self):
        self.dynamo_resource = boto3.resource(
            'dynamodb', "us-east-2",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID_brainbug", None),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY_brainbug", None))
        self.slack_table_name = "slack_apps"
        self.partition_key = "conversions_oncall-rotation"
        self.schedule_sort_key = "schedule_current"
        self.partition_key_name = "app_pKey"
        self.sort_key_name = "sortKey"
        self.slack_table = self.dynamo_resource.Table(self.slack_table_name)

    def get_schedule(self):
        dynamo_response = self.__query(
            Key(self.partition_key_name).eq(self.partition_key) & Key(self.sort_key_name).eq(self.schedule_sort_key))
        schedule_record = dynamo_response.get('Items')
        return schedule_record[0] if schedule_record else self.create_schedule()

    def put_schedule(self, schedule_record: dict):
        self.slack_table.put_item(Item=schedule_record)

    def get_user(self, user_id: str):
        dynamo_response = self.__query(
            Key(self.partition_key_name).eq(self.partition_key) & Key(self.sort_key_name).eq(user_id))
        user_record = dynamo_response.get('Items')
        return user_record[0] if user_record else self.create_user(user_id)

    def put_user(self, user_record: dict):
        self.slack_table.put_item(Item=user_record)

    def delete_user(self, user_id):
        self.slack_table.delete_item(
            Key=
            {
                self.partition_key_name: self.partition_key,
                self.sort_key_name: user_id
            }
        )

    def create_schedule(self, user_ids=[]):
        return asdict(Schedule(self.partition_key, self.schedule_sort_key, user_ids, date.today().strftime("%d/%m/%Y")))

    def create_user(self, user_id):
        return asdict(User(self.partition_key, user_id, []))

    def __query(self, key_condition_expression, log=logging):
        dynamo_response = self.slack_table.query(
            Limit=1,
            ConsistentRead=True,
            KeyConditionExpression=key_condition_expression
        )
        log.info(dynamo_response)
        return dynamo_response
