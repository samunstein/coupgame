import unittest
from unittest import TestCase

from game.enums.cards import Contessa, Assassin
from game.gameserver import Game
from game.messages.responses import AssassinateDecision, IncomeDecision
from tests.mocks.mock_connection import get_server_mock_connection
from tests.mocks.mock_logic import MockLogic


class Methods:
    @staticmethod
    def assassinate_if_money(self: MockLogic):
        if self.get_state().money >= 3:
            return AssassinateDecision(list(self.get_state().alive_opponents().keys())[0])
        else:
            return IncomeDecision()


class AssassinTest(TestCase, Methods):
    def test_basic_no_blocks(self):
        clients = [get_server_mock_connection(MockLogic(Methods.assassinate_if_money, False, False, False)) for _ in
                   range(2)]
        game = Game(clients)
        game.setup_players()

        self.assertEqual(game.rule_abiding_players[0].money, 2)
        self.assertEqual(game.rule_abiding_players[1].money, 2)

        self.assertEqual(len(game.rule_abiding_players[0].cards), 2)
        self.assertEqual(len(game.rule_abiding_players[1].cards), 2)

        game.run_one_turn()

        self.assertEqual(game.rule_abiding_players[0].money, 3)
        self.assertEqual(game.rule_abiding_players[1].money, 2)

        game.run_one_turn()

        self.assertEqual(game.rule_abiding_players[0].money, 3)
        self.assertEqual(game.rule_abiding_players[1].money, 3)

        game.run_one_turn()

        self.assertEqual(game.rule_abiding_players[0].money, 0)
        self.assertEqual(len(game.rule_abiding_players[1].cards), 1)

    def test_challenge_no_block(self):
        clients = [get_server_mock_connection(MockLogic(Methods.assassinate_if_money, True, False, False)) for _ in
                   range(2)]
        game = Game(clients, deck=[Contessa()] * 4)
        game.setup_players()
        game.rule_abiding_players[0].give_money(1)
        game.rule_abiding_players[1].give_money(1)
        game.rule_abiding_players[1].give_card(Assassin())
        game.rule_abiding_players[1].remove_card(Contessa())
        # Leaves the second player with contessa and assassin

        game.run_one_turn()

        # First player was rightfully challenged and lost a card but no money
        self.assertEqual(game.rule_abiding_players[0].money, 3)
        self.assertEqual(len(game.rule_abiding_players[1].cards), 2)
        self.assertEqual(len(game.rule_abiding_players[0].cards), 1)

        game.run_one_turn()
        # Second player was wrongfully challenged, and the first player lost a card and died. The deck is empty, but
        # the assassin in the second player's hand gets first returned and then given back.
        self.assertEqual(len(game.alive_players), 1)
        n = list(game.alive_players)[0]
        self.assertEqual(game.alive_players[n].number, 1)
        self.assertEqual(game.alive_players[n].money, 0)
        self.assertEqual(game.alive_players[n].cards, [Contessa(), Assassin()])

    def test_insta_die(self):
        clients = [get_server_mock_connection(MockLogic(Methods.assassinate_if_money, True, False, False)) for _ in
                   range(2)]
        game = Game(clients, deck=[Assassin()] * 5)
        game.setup_players()
        game.rule_abiding_players[0].give_money(1)

        game.run_one_turn()
        self.assertEqual(len(game.alive_players), 1)
        n = list(game.alive_players)[0]
        self.assertEqual(game.alive_players[n].number, 0)
        self.assertEqual(game.alive_players[n].money, 0)

    def test_blocking(self):
        logic0 = MockLogic(Methods.assassinate_if_money, False, True, False)
        logic1 = MockLogic(Methods.assassinate_if_money, False, True, False)
        clients = [get_server_mock_connection(logic0), get_server_mock_connection(logic1)]
        game = Game(clients)
        game.setup_players()
        game._money_change(game.rule_abiding_players[0], 1)
        game._money_change(game.rule_abiding_players[1], 1)

        game.run_one_turn()
        self.assertEqual(game.rule_abiding_players[0].money, 0)
        self.assertEqual(logic0.get_state().money, 0)
        self.assertEqual(logic1.get_state().opponents[0].money, 0)
        self.assertEqual(len(game.rule_abiding_players[0].cards), 2)
        self.assertEqual(len(game.rule_abiding_players[1].cards), 2)

    def test_block_challenge(self):
        # Unsuccessful challenge
        clients = [get_server_mock_connection(MockLogic(Methods.assassinate_if_money, False, True, True)) for _ in
                   range(2)]
        game = Game(clients, deck=[Contessa()] * 4)
        game.setup_players()
        game.rule_abiding_players[0].give_money(1)

        game.run_one_turn()
        self.assertEqual(game.rule_abiding_players[0].money, 0)
        self.assertEqual(len(game.rule_abiding_players[0].cards), 1)
        self.assertEqual(len(game.rule_abiding_players[1].cards), 2)

        # Successful challenge
        clients = [get_server_mock_connection(MockLogic(Methods.assassinate_if_money, False, True, True)) for _ in
                   range(2)]
        game = Game(clients, deck=[Assassin()] * 4)
        game.setup_players()
        game.rule_abiding_players[0].give_money(1)

        game.run_one_turn()
        self.assertEqual(game.rule_abiding_players[0].money, 0)
        self.assertEqual(len(game.alive_players), 1)
        n = list(game.alive_players)[0]
        self.assertEqual(len(game.rule_abiding_players[n].cards), 2)
        self.assertEqual(game.alive_players[n].number, 0)


if __name__ == '__main__':
    unittest.main()
