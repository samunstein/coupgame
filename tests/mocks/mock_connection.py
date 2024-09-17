from Tools.scripts.generate_token import make_c

from common.common import make_command_params
from config import PARAM_SPLITTER, COMMAND_END
from connection.common import Connection
from game.gameclient import PlayerClient
from game.logic.clients import ClientLogic


class ServerMockConnection(Connection):
    def __init__(self, gameclient: PlayerClient):
        self.client = gameclient

    def send(self, *msg):
        return self.client.run_command(msg[0], msg[1:])

    def receive(self):
        pass

    def send_and_receive(self, *msg):
        res = self.send(*msg)
        if isinstance(res, tuple|list):
            return make_command_params(*res)
        else:
            return make_command_params(res)

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
