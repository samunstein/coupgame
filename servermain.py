from connection.server import get_connections
from game.gameserver import Game

if __name__ == "__main__":
    connections = get_connections(2)
    game = Game(connections)
    game.run()
