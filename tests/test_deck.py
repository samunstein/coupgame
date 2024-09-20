import unittest
from unittest import TestCase

from config import EACH_CARD_IN_DECK
from game.enums.cards import Card, Ambassador, Assassin, Contessa
from game.gameserver import Game
from game.messages.responses import AmbassadateDecision
from tests.mocks.mock_connection import get_server_mock_connection
from tests.mocks.mock_logic import MockLogic


class Methods:
    @staticmethod
    def always_ambassador(self: MockLogic):
        return AmbassadateDecision()

class DeckTest(TestCase, Methods):
    def test_basic_ambassador(self):
        clients = [get_server_mock_connection(MockLogic(Methods.always_ambassador, False, False, False)) for _ in range(2)]
        game = Game(clients, deck=[Ambassador()] * 6)
        game.setup_players()

        game.run_one_turn()
        self.assertEqual(game.players[0].money, 2)
        self.assertEqual(game.players[1].money, 2)
        self.assertEqual(len(game.players[0].cards), 2)
        self.assertEqual(len(game.players[1].cards), 2)

    def test_deck_state(self):
        clients = [get_server_mock_connection(MockLogic(Methods.always_ambassador, False, False, False)) for _ in range(2)]
        game = Game(clients)
        game.setup_players()

        game.run_one_turn()
        all_cards_in_play = game.deck + game.players[0].cards + game.players[1].cards
        for c in Card.all():
            self.assertEqual(all_cards_in_play.count(c), EACH_CARD_IN_DECK)

    def test_controlled_deck_state(self):
        clients = [get_server_mock_connection(MockLogic(Methods.always_ambassador, False, False, False)) for _ in range(2)]
        game = Game(clients, deck=[Ambassador()] * 6)
        game.setup_players()
        game.players[0].remove_card(Ambassador())
        game.players[0].remove_card(Ambassador())
        game.players[0].give_card(Assassin())
        game.players[0].give_card(Assassin())
        game.run_one_turn()

        self.assertEqual(game.players[0].cards, [Ambassador()] * 2)
        self.assertEqual(game.deck, [Assassin()] * 2)

    def test_failed_challenge_ambassador(self):
        clients = [get_server_mock_connection(MockLogic(Methods.always_ambassador, True, False, False)) for _ in range(2)]
        game = Game(clients, deck=[Ambassador()] * 6)
        game.setup_players()
        game.players[1].remove_card(Ambassador())
        game.players[1].remove_card(Ambassador())
        game.players[1].give_card(Assassin())
        game.players[1].give_card(Assassin())
        game.deck = [Contessa()] * 2
        # Deck: 2 contessa, Player 0: 2 ambassadors, Player 1: 2 assassins
        game.run_one_turn()

        # Player 1 loses a card. Player 0 reveals amb and gets something back. Then Player 0's ambassador goes through,
        # giving them either one or two contessas (depending on what the reveal gave them), which will stick in hand.
        self.assertEqual(game.players[1].cards, [Assassin()])
        self.assertEqual(1 <= game.players[0].cards.count(Contessa()) <= 2, True)

        all_cards_in_play: list[Card] = game.deck + game.players[0].cards + game.players[1].cards
        self.assertEqual(all_cards_in_play.count(Contessa()), 2)
        self.assertEqual(all_cards_in_play.count(Ambassador()), 2)
        self.assertEqual(all_cards_in_play.count(Assassin()), 1)





if __name__ == '__main__':
    unittest.main()