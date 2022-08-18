import os
from abc import ABC, abstractmethod
from datetime import date

from .dynamo_db import DynamoDb
from .exceptions import UsageException
import app.models


class Command(ABC):
    def __init__(self):
        self.dynamo_db = DynamoDb()

    @abstractmethod
    def execute(self, respond, client) -> None:
        pass

    @staticmethod
    def is_valid_user(users, valid_users):
        is_valid = True
        for user_id in users:
            is_valid = is_valid and user_id in valid_users
        return is_valid


class NextCommand(Command):
    def __init__(self):
        super().__init__()

    def execute(self, respond, client) -> None:
        # rotate schedule
        schedule_record = self.dynamo_db.get_schedule()
        rotation_list: list = schedule_record['rotation']
        self.rotate_schedule(rotation_list)

        # update schedule
        current_on_call_start_dt = schedule_record['start_dt']
        today = date.today().strftime("%m/%d/%Y")
        self.update_schedule(schedule_record, today)

        # update user
        current_on_call = rotation_list[-1]
        user_record = self.dynamo_db.get_user(current_on_call)
        self.update_user(user_record, current_on_call_start_dt, today)

        new_on_call = rotation_list[0]
        post_to_conversions_channel(client, f"<@{new_on_call}> is now on-call for the monthly batch.")
        direct_message_user(client, new_on_call, "You are now on-call for the monthly batch.")

    @staticmethod
    def rotate_schedule(rotation_list: list):
        if len(rotation_list) == 0 or len(rotation_list) == 1:
            raise UsageException("Rotation must contain at least two users before calling 'next'.")
        rotation_list.append(rotation_list.pop(0))

    def update_schedule(self, schedule_record, start_dt):
        schedule_record['start_dt'] = start_dt
        self.dynamo_db.put_schedule(schedule_record)

    def update_user(self, user_record, start_dt, end_dt):
        history: list = user_record.get('History')
        history.append(app.models.create_history_item(start_dt, end_dt))
        self.dynamo_db.put_user(user_record)


class ShowCommand(Command):
    def __init__(self):
        super().__init__()

    def execute(self, respond, client) -> None:
        schedule_record = self.dynamo_db.get_schedule()
        response = ', '.join(f"<@{uid}>" for uid in schedule_record['rotation'])
        respond(response)


class SwapCommand(Command):
    def __init__(self, user1, user2):
        super().__init__()
        self.user1 = user1
        self.user2 = user2

    def execute(self, respond, client) -> None:
        if self.user1 is None or self.user2 is None:
            raise UsageException("Invalid user argument.")

        schedule_record = self.dynamo_db.get_schedule()
        rotation_list: list = schedule_record['rotation']

        if not self.is_valid_user([self.user1, self.user2], rotation_list):
            raise UsageException("Cannot perform 'swap' with an unknown user.")

        # perform the swap
        user1_idx = rotation_list.index(self.user1)
        rotation_list[rotation_list.index(self.user2)] = self.user1
        rotation_list[user1_idx] = self.user2
        self.dynamo_db.put_schedule(schedule_record)

        post_to_conversions_channel(client, f"<@{self.user1}> and <@{self.user2}> have been swapped in the schedule.")


class HistoryCommand(Command):
    def __init__(self, user):
        super().__init__()
        self.user = user

    def execute(self, respond, client) -> None:
        if self.user is None:
            raise UsageException("Invalid user argument.")

        schedule_record = self.dynamo_db.get_schedule()
        if not self.is_valid_user([self.user], schedule_record['rotation']):
            raise UsageException("User does not exist.")

        user_record = self.dynamo_db.get_user(self.user)
        history: list = user_record.get('History')

        if history is None or len(history) == 0:
            respond("User has no history.")
        else:
            respond(os.linesep.join(f"{entry.get('start_dt')} - {entry.get('end_dt')}" for entry in history))


class AddCommand(Command):
    def __init__(self, user):
        super().__init__()
        self.user = user

    def execute(self, respond, client) -> None:
        if self.user is None:
            raise UsageException("Invalid user argument.")

        schedule_record = self.dynamo_db.get_schedule()

        if self.is_valid_user([self.user], schedule_record['rotation']):
            raise UsageException("User already exists.")

        schedule_record['rotation'].append(self.user)
        self.dynamo_db.put_schedule(schedule_record)

        respond("Successfully added user to the schedule.")
        post_to_conversions_channel(client, f"<@{self.user}> has been added to the schedule.")


class RemoveCommand(Command):
    def __init__(self, user):
        super().__init__()
        self.user = user

    def execute(self, respond, client) -> None:
        if self.user is None:
            raise UsageException("Invalid user argument.")

        schedule_record = self.dynamo_db.get_schedule()

        if not self.is_valid_user([self.user], schedule_record['rotation']):
            raise UsageException("User does not exist.")

        schedule_record['rotation'].remove(self.user)
        self.dynamo_db.put_schedule(schedule_record)
        self.dynamo_db.delete_user(self.user)

        respond("Successfully removed user from the schedule.")
        post_to_conversions_channel(client, f"<@{self.user}> has been removed from the schedule.")


def post_to_conversions_channel(client, message):
    client.chat_postMessage(channel='conversions-dev', text=message)


def direct_message_user(client, user_id, message):
    client.chat_postMessage(channel=user_id, text=message)
