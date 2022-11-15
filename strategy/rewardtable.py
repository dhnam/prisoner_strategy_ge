from dataclasses import dataclass
from .response import Response


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