from abc import ABC, abstractmethod
from typing import Callable
import pickle
from anytree import Node
from anytree.exporter import DotExporter
from strategy.basic_config import *
from strategy.strategy import Strategy

class Environment(ABC):
    def __init__(self, size: int, logging: bool=True):
        self._size: int = size
        self.population: list[Strategy] = []
        for next_population in range(size):
            self.population.append(Strategy(f"Gen0_{next_population}"))

        self.scores: list[float] = [0] * size
        self.generation: int = 0
        self.logging = logging
        if logging:
            self.log = self.population.copy()

    @property
    def size(self) -> int:
        return self._size

    @abstractmethod
    def generation_processing(self):
        pass

    @abstractmethod
    def next_generation(self):
        pass

    def export_history_diagram(self, file_path: str, nodename_func: Callable[[Node], str]=lambda x: x.short_str):
        if not self.logging:
            return
        root = Node("")
        root.children = self.log
        def nodename(x: Node):
            if not isinstance(x, Strategy):
                return x.name
            return nodename_func(x)
        DotExporter(root, nodenamefunc=nodename).to_picture(file_path)

    def export_log(self, file_path: str):
        with open(file_path, 'wb') as f:
            pickle.dump(self.log, f)
