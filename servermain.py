from config import PLAYER_AMOUNT
from connection.server import get_connections
from game.gameserver import Game

if __name__ == "__main__":
    connections = get_connections(PLAYER_AMOUNT)
    game = Game(connections)
    game.run()
