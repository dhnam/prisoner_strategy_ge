from .strategy import Strategy, Manager, State, DetrTransition, BinarySelector
from .response import Response

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