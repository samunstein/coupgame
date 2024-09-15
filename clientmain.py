from config import HOST, PORT
from connection.common import OpenSocket
from game.gameclient import PlayerClient
from game.logic.clients import ExtremelySimpleTestClient

if __name__ == "__main__":
    connection = OpenSocket.new(HOST, PORT)
    logic = ExtremelySimpleTestClient()
    client = PlayerClient(connection, logic)
    client.run()
