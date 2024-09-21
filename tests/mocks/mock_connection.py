from connection.common import Connection
from game.gameclient import PlayerClient
from game.logic.clients import ClientLogic
from game.messages.commands import Command


class ServerMockConnection(Connection):
    def __init__(self, gameclient: PlayerClient):
        self.client = gameclient

    def send(self, command: Command):
        return self.client.run_command(command)

    def receive(self):
        pass

    def send_and_receive(self, command: Command) -> str:
        res = self.send(command)
        if res is not None:
            return res.serialize()

    def close(self):
        pass


class DummyConnection(Connection):
    def __init__(self):
        pass

    def send(self, *msg):
        pass

    def receive(self):
        pass

    def send_and_receive(self, *msg):
        pass

    def close(self):
        pass


def get_server_mock_connection(logic: ClientLogic) -> ServerMockConnection:
    return ServerMockConnection(PlayerClient(DummyConnection(), logic))
