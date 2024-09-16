from config import PLAYER_AMOUNT
from connection.server import get_connections
from game.gameclient import PlayerClient
from game.gameserver import Game
from game.logic.clients import ExtremelySimpleTestClient
from tests.mocks.mock_connection import ServerMockConnection, DummyConnection

if __name__ == "__main__":
    connections = [ServerMockConnection(PlayerClient(DummyConnection(), ExtremelySimpleTestClient())),
                   ServerMockConnection(PlayerClient(DummyConnection(), ExtremelySimpleTestClient()))]
    # connections = get_connections(PLAYER_AMOUNT)
    game = Game(connections)
    game.run()
