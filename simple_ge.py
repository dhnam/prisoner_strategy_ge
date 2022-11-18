from itertools import combinations_with_replacement
import random
from strategy.basic_config import *
from strategy.strategy import Strategy
from strategy.duel import Duel

class Environment:
    def __init__(self, size: int):
        self._size: int = size
        self.population: list[Strategy] = []
        for next_population in range(size):
            self.population.append(Strategy(f"Gen0_{next_population}"))

        self.scores: list[float] = [0] * size
        self.generation: int = 0

    @property
    def size(self) -> int:
        return self._size

    def generation_processing(self):
        for (strt1_idx, strt1), (strt2_idx, strt2) in combinations_with_replacement(enumerate(self.population), 2):
            strt1_final_reward = 0
            strt2_final_reward = 0
            for _, (reward1, reward2) in Duel(strt1, strt2, REWARD_TABLE, DUEL_LENGTH):
                strt1_final_reward = reward1
                strt2_final_reward = reward2
            self.scores[strt1_idx] = strt1_final_reward
            self.scores[strt2_idx] = strt2_final_reward

    def next_generation(self):
        # stratage: 100%: percentage-based
        parents = random.choices(self.population, self.scores, k=len(self.size))
        self.population = []
        for next_parent in parents:
            self.population.append(next_parent.clone().mutate(MUTATE_RATE))

        self.scores = [0] * self.size




if __name__ == "__main__":

    # Loop
    population = int(input("Input population: "))
    env = Environment(population)
    gen: int = 0
    env.generation_processing()
    while True:
        # Menu: process, show top, ...?
        print(f"====GENERATION {gen}====")
        menu = input("Process: p, Show nth: (input number), Show score: s\ninput: ")
        if menu == "p":
            gen += 1
            env.next_generation()
            env.generation_processing()
        if menu.isdigit() and int(menu) < population:
            print(env.population[int(menu)])
        if menu == "s":
            print(env.scores)
