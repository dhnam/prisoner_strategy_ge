from tqdm import tqdm
from environment import Environment
import strategy.sample_strategy
from strategy.duel import Duel
from strategy.basic_config import *

def test(env_class: type[Environment]):
    population = int(input("Input population: "))
    env = env_class(population)
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