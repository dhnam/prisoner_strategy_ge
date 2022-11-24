from .strategy import Strategy, Manager, State, DetrTransition, BinarySelector
from .response import Response
from .duel import Duel
from .rewardtable import RewardTable

class AlwaysCoopStrategy(Strategy):
    def __init__(self, name="AlwaysCoop"):
        self.name = name
        states: list[State] = [State.from_predefined(
            0,
            DetrTransition(Response.COOPERATE, Response.COOPERATE, 0),
            DetrTransition(Response.BETRAYAL, Response.COOPERATE, 0),
        )]
        self.manager = Manager.from_state_list(states)
        self.first_move = BinarySelector((Response.COOPERATE, Response.COOPERATE), (1, 0))

class AlwaysBetrStrategy(Strategy):
    def __init__(self, name="AlwaysBetr"):
        self.name = name
        states: list[State] = [State.from_predefined(
            0,
            DetrTransition(Response.COOPERATE, Response.BETRAYAL, 0),
            DetrTransition(Response.BETRAYAL, Response.BETRAYAL, 0),
        )]
        self.manager = Manager.from_state_list(states)
        self.first_move = BinarySelector((Response.BETRAYAL, Response.BETRAYAL), (1, 0))

class TFTStrategy(Strategy):
    def __init__(self, name="TitForTat"):
        self.name = name
        states: list[State] = [State.from_predefined(
            0,
            DetrTransition(Response.COOPERATE, Response.COOPERATE, 0),
            DetrTransition(Response.BETRAYAL, Response.BETRAYAL, 0),
        )]
        self.manager = Manager.from_state_list(states)
        self.first_move = BinarySelector((Response.COOPERATE, Response.COOPERATE), (1, 0))

class StrategyTester:
    def __init__(self, strategy_to_test:Strategy, reward_table:RewardTable, duel_length:int):
        self.strategy_to_test = strategy_to_test
        self.test_strategy = [
            AlwaysCoopStrategy(),
            AlwaysBetrStrategy(),
            TFTStrategy(),
            strategy_to_test
        ]
        self.reward_table = reward_table
        self.duel_length = duel_length

    def print_test(self):
        for next_test in self.test_strategy:
            print(f"{self.strategy_to_test.name} VS {next_test.name}")
            for i, (next_response, next_reward) in enumerate(Duel(self.strategy_to_test, next_test, self.reward_table, self.duel_length)):
                print(f"{i}: {next_response}, {next_reward}")