from strategy.basic_config import *
from strategy.strategy import Strategy
from strategy.duel import Duel
from itertools import combinations_with_replacement

class Environment:
    def __init__(self, size: int):
        self.population: list[Strategy] = []
        for next_population in range(size):
            self.population.append(Strategy(f"Gen0_{next_population}"))

        self.scores: list[float] = [0] * size
        self.generation: int = 0

    def generation_processing(self):
        for (strt1_idx, strt1), (strt2_idx, strt2) in combinations_with_replacement(enumerate(self.population), 2):
            strt1_final_reward = 0
            strt2_final_reward = 0
            for _, (reward1, reward2) in Duel(strt1, strt2):
                strt1_final_reward = reward1
                strt2_final_reward = reward2
            self.scores[strt1_idx] = strt1_final_reward
            self.scores[strt2_idx] = strt2_final_reward




if __name__ == "__main__":
    env = Environment(2)
    env.generation_processing()
    print(env.scores)

