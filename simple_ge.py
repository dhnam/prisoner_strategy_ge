from itertools import combinations_with_replacement
import random
from tqdm import tqdm
from strategy.basic_config import *
from strategy.strategy import Strategy
from strategy.duel import Duel
import strategy.sample_strategy

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
        parents = random.choices(self.population, self.scores, k=self.size)
        self.population = []
        self.generation += 1
        for i, next_parent in enumerate(parents):
            child = Strategy.clone(next_parent).mutate(MUTATE_RATE)
            child.name = f"Gen{self.generation}_{i}_base{next_parent.name.split('_base')[0]}"
            self.population.append(child)

        self.scores = [0] * self.size




if __name__ == "__main__":

    # Loop
    population = int(input("Input population: "))
    env = Environment(population)
    gen: int = 0
    env.generation_processing()
    sample_strategies = [
        strategy.sample_strategy.AlwaysCoopStrategy(),
        strategy.sample_strategy.AlwaysBetrStrategy(),
        strategy.sample_strategy.TFTStrategy(),
        None
        ]
    print(f"====GENERATION {gen}====")
    while True:
        # Menu: process, show top, ...?
        menu = input("Process: p(+num), Show nth: (input number), Show score: s, Ordered: o, Sample duel: S(num)\ninput: ")
        try:
            if menu[0] == "p":
                if len(menu[1:]) == 0:
                    forward = 1
                else:
                    forward = int(menu[1:])
                for _ in tqdm(range(forward)):
                    gen += 1
                    env.next_generation()
                    env.generation_processing()
                print(f"====GENERATION {gen}====")
            if menu.isdigit() and int(menu) < population:
                print(env.population[int(menu)])
            if menu == "s":
                print(env.scores)
            if menu == "o":
                print([x for _, x in sorted(zip(env.scores, range(population)), reverse=True)])
            if menu[0] == "S":
                strt_1 = env.population[int(menu[1:])]
                sample_strategies[-1] = strt_1
                for strt_2 in sample_strategies:
                    print(f"{strt_1.name} VS {strt_2.name}")
                    for i, (next_response, next_reward) in enumerate(Duel(strt_1, strt_2, REWARD_TABLE, DUEL_LENGTH)):
                        print(f"{i}: {next_response}, {next_reward}")
        except ValueError:
            print("Invalid input. Please Try again.")

