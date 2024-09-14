from config import HOST, PORT
from connection.common import OpenSocket
from game.gameclient import PlayerClient
from game.logic.clients import ConsoleClient

if __name__ == "__main__":
    connection = OpenSocket.new(HOST, PORT)
    logic = ConsoleClient()
    client = PlayerClient(connection, logic)
    client.run()
