from abc import ABC, abstractmethod
from strategy.basic_config import *
from strategy.strategy import Strategy

class Environment(ABC):
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

    @abstractmethod
    def generation_processing(self):
        pass

    @abstractmethod
    def next_generation(self):
        pass