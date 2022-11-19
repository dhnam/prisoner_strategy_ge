from itertools import combinations_with_replacement
import random
from strategy.basic_config import *
from strategy.strategy import Strategy
from strategy.duel import Duel
from environment import Environment
import env_test

class SimpleEnvironment(Environment):
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
    env_test.test(SimpleEnvironment)

