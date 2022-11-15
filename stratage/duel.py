from __future__ import annotations
from stratage import *
from pathlib import Path

REWARD_TABLE: RewardTable

@dataclass
class RewardTable:
    coop_coop: float
    coop_betr: float
    betr_coop: float
    betr_betr: float

    def get_rewards(self, resp_a: Response, resp_b: Response) -> tuple[float, float]:
        if (resp_a, resp_b) == (Response.COOPERATE, Response.COOPERATE):
            return self.coop_coop, self.coop_coop
        if (resp_a, resp_b) == (Response.COOPERATE, Response.BETRAYAL):
            return self.coop_betr, self.betr_coop
        if (resp_a, resp_b) == (Response.BETRAYAL, Response.COOPERATE):
            return self.betr_coop, self.coop_betr
        return self.betr_betr, self.betr_betr


class Duel:
    def __init__(self, strategy_a: Strategy, strategy_b: Strategy, reward_table: RewardTable, iter_length: int):
        self.strategy_a = strategy_a
        self.strategy_b = strategy_b
        self.reward_table = reward_table
        self.iter_length = iter_length
        self.rewards: tuple[float, float] = (0, 0)
        self.last_responses: tuple[Response, Response] = (None, None)

    def __iter__(self):
        self._iter_cnt = 0
        self.strategy_a.reset()
        self.strategy_b.reset()
        self.rewards: tuple[float, float] = (0, 0)
        return self

    def __next__(self) -> tuple[tuple[Response, Response], tuple[float, float]]:
        if self._iter_cnt >= self.iter_length:
            raise StopIteration

        if self._iter_cnt == 0:
            responses = (self.strategy_a.make_first_move(), self.strategy_b.make_first_move())
        else:
            responses = (self.strategy_a.make_response(self.last_responses[1]), self.strategy_b.make_response(self.last_responses[0]))
        self.last_responses = responses
        reward_a, reward_b = self.reward_table.get_rewards(*responses)
        new_rewards = (self.rewards[0] + reward_a, self.rewards[1] + reward_b)
        self.rewards = new_rewards
        self._iter_cnt += 1
        return responses, self.rewards

config_path = Path(__file__).with_name('config.json')
with open(config_path, 'r') as f:
    setting = json.load(f)
    REWARD_TABLE = RewardTable(**setting["REWARD_TABLE"])