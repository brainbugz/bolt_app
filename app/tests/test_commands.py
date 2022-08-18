from unittest.mock import patch, Mock

import pytest
from app.commands import NextCommand
from app.exceptions import UsageException
from app.dynamo_db import DynamoDb


@patch('app.dynamo_db.DynamoDb.get_schedule')
def test_next_exception(mock_get_schedule):
    mock_get_schedule.return_value = DynamoDb().create_schedule(["12345"])
    next_cmd = NextCommand()
    with pytest.raises(UsageException, match="Rotation must contain at least two users before calling 'next'") as e:
        next_cmd.execute(Mock(), Mock())

