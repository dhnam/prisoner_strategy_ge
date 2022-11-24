import pickle
import difflib
from anytree import Node, ZigZagGroupIter
from strategy.strategy import Strategy
from strategy.sample_strategy import StrategyTester
from strategy.basic_config import DUEL_LENGTH, REWARD_TABLE

class LogExplorer:
    def __init__(self, path: str):
        with open(path, 'rb') as f:
            self.log: list[Strategy] = pickle.load(f)
        root = Node("")
        root.children = self.log
        self._generation: int = 0
        existed_population_unsorted: list[list[Strategy]] = list(ZigZagGroupIter(root))[1:]
        self.existed_populations = [sorted(x, key=LogExplorer.index_of)
                            for x in existed_population_unsorted]

    
    @staticmethod
    def index_of(strt: Strategy) -> int:
        return int(strt.name.split("_")[1])

    @property
    def last_generation(self) -> int:
        return len(self.existed_populations) - 1

    @property
    def generation(self) -> int:
        return self._generation

    @generation.setter
    def generation(self, new_generation: int):
        if not isinstance(new_generation, int):
            raise ValueError("Generation should be integer.")
        if new_generation > self.last_generation:
            raise IndexError(f"Generation {new_generation} is not available (maximum: {self.last_generation}).")
        if new_generation < 0:
            raise IndexError(f"Generation should be positive or zero, not {new_generation}.")

        self._generation = new_generation

    @property
    def population(self) -> int:
        return len(self.existed_populations[0])

    def from_index(self, idx: int) -> Strategy:
        return self.existed_populations[self.generation][idx]

    def parent_of(self, idx: int) -> Strategy:
        if self.generation == 0:
            raise IndexError("Root index does not have parent.")
        return self.from_index(idx).parent

    def diff(self, strt1_addr: tuple[int, int], strt2_addr: tuple[int, int]) -> str:
        str1 = str(self.existed_populations[strt1_addr[0]][strt1_addr[1]]).splitlines()[2:-1]
        str2 = str(self.existed_populations[strt2_addr[0]][strt2_addr[1]]).splitlines()[2:-1]
        return '\n'.join(difflib.Differ().compare(str1, str2))
        # TODO: Playing with this differ...

    def diff_parent(self, idx: int) -> str:
        return self.diff(
            (self.generation - 1, LogExplorer.index_of(self.parent_of(idx))),
            (self.generation, idx)
        )

if __name__ == "__main__":
    path = input("pickle file path: ")
    explorer = LogExplorer(path)
    print(f"Population: {explorer.population}")
    print(f"====GENERATION {explorer.generation}/{explorer.last_generation}====")
    while True:
        print("Change generation: g(num), Show nth: (input number), Sample duel: S(num), Diff with parent: D(num)")
        menu = input("input: ")
        if menu[0] == "g":
            explorer.generation = int(menu[1:])
            print(f"====GENERATION {explorer.generation}/{explorer.last_generation}====")
        if menu.isdigit() and int(menu) < explorer.population:
            print(explorer.from_index(int(menu)))
        if menu[0] == "S":
            strt = explorer.from_index(int(menu[1:]))
            tester = StrategyTester(strt, REWARD_TABLE, DUEL_LENGTH)
            tester.print_test()
        if menu[0] == "D":
            print(explorer.diff_parent(int(menu[1:])))
