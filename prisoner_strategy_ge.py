from enum import Enum, auto
from abc import ABC
from typing import TypeVar, Generic
from random import choices

# Classes: Strategy / State / Transition / Manager

class State:
    def __init__(self, state_num: int):
        self.state_num = state_num

class Response(Enum):
    COOPERATE = auto()
    BETRAYAL = auto()

T = TypeVar('T')

class BinarySelector(Generic[T]):
    def __init__(self, options: tuple[T, T], prob: tuple[float, float]):
        self.options = options
        self._prob = prob
        assert sum(prob) == 1.

    @property
    def prob(self):
        return self._prob

    @prob.setter
    def prob(self, new_prob: tuple[float, float]):
        assert sum(new_prob) == 1.
        self._prob = new_prob

    def select() -> T:
        return choices(options, weights=self._prob)[0]

class Transition:
    # Transition: counterpart_response / my_response / is_linked / next_state
    # DetrTransition: counterpart_response / my_response / next_state
    def __init__(self, counterpart_response: Response, my_response: BinarySelector[Response], is_linked: bool, next_state: BinarySelector[int]):
        self.counterpart_response = counterpart_response
        self.my_response = my_response
        self.is_linked = is_linked
        self.next_state = next_state
        if is_linked:
            next_state.prob = my_response.prob

    def response_state(self):


class DetrTransition: