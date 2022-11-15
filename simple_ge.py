from stratage.basic_config import *
from stratage import Stratage
from duel import Duel

class Environment:
    def __init__(self, size: int):
        self.population: list[Stratage] = []
        for next_population in range(size):
            self.population.append(Stratage(f"Gen0_{next_population}"))

if __name__ == "__main__":
    env = Environment(2)
    for i, (next_response, next_reward) in enumerate(Duel(env.population[0], env.population[1], REWARD_TABLE, 10)):
        print(f"{i}: {next_response}, {next_reward}")

