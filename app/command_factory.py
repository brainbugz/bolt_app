from .commands import NextCommand, SwapCommand, ShowCommand, HistoryCommand, AddCommand, RemoveCommand
from .exceptions import UsageException


class CommandFactory:
    @staticmethod
    def get_command(command_name, users):
        user1 = users[0] if len(users) > 0 else None
        user2 = users[1] if len(users) > 1 else None

        if command_name == "next":
            return NextCommand()
        elif command_name == "swap":
            return SwapCommand(user1, user2)
        elif command_name == "show":
            return ShowCommand()
        elif command_name == "history":
            return HistoryCommand(user1)
        elif command_name == "add":
            return AddCommand(user1)
        elif command_name == "remove":
            return RemoveCommand(user1)
        else:
            raise UsageException(f"Unknown command: {command_name}")
