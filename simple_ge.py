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
            for _, (reward1, reward2) in Duel(strt1, strt2, REWARD_TABLE, DUEL_LENGTH):
                strt1_final_reward = reward1
                strt2_final_reward = reward2
            self.scores[strt1_idx] = strt1_final_reward
            self.scores[strt2_idx] = strt2_final_reward

    def new_generation(self):
        # stratage: 50% -> last gen, 50%: percentage-based
        self.scores = [0] * size




if __name__ == "__main__":

    # Loop
    population = int(input("Input population: "))
    env = Environment(population)
    gen = 0
    while True:
        # Menu: process, show top, ...?
        print(f"====GENERATION {gen}====")
        menu = input("Process: p, Show nth: (input number), Show score: s")
        if menu == "p":
            env.generation_processing()
        if menu.isdigit() and int(menu) < population:
            print(self.population[int(menu)])
        if menu == "s":
            print(self.scores)
