from __future__ import annotations
from enum import Enum, auto
from abc import ABC
from typing import TypeVar, Generic, Self
from random import choices, choice, random, sample

# Classes: Strategy / State / Transition / Manager

# TODO: separate this to external file
RANDOM_DETR_STATE_RATIO = 0.1

TransitionType = TypeVar('TransitionType', bound='Transition')

class State:
    def __init__(self, state_num: int, manager: Manager):
        self.state_num = state_num
        self.manager = manager
        self.state_transitions: dict[Response, TransitionType] = {}
        for next_response in Response:
            self.point_mutate_transition(next_response, initing_state=True)

    def __str__(self):
        ret_str = f"State {self.state_num}\n"
        ret_str += "{\n"
        for next_response in Response:
            ret_str += f"\t{self.state_transitions[next_response]}\n"
        ret_str += "}"
        return ret_str

    def point_mutate_transition(self, response: Response, initing_state: bool=False):
        state_candidates = manager.get_state_candidates(initing_state=initing_state)
        transition_type: type[TransitionType] = Transition
        if random() > RANDOM_DETR_STATE_RATIO:
            transition_type = DetrTransition
        self.state_transitions[response] = transition_type.get_random_of(response, state_candidates)

    def response_state(self, counterpart_response: Response) -> tuple[Response, int]:
        return self.state_transitions[counterpart_response].response_state()


class Response(Enum):
    COOPERATE = auto()
    BETRAYAL = auto()
    def __str__(self):
        if self.name == 'BETRAYAL':
            return "B"
        if self.name == "COOPERATE":
            return "C"
        raise TypeError

T = TypeVar('T')

class BinarySelector(Generic[T]):
    def __init__(self, options: tuple[T, T], prob: tuple[float, float]):
        self.options = options
        self._prob = prob
        assert sum(prob) == 1.

    def __str__(self):
        if max(self.prob) != 1.:
            return f"({self.options[0]}({self.prob[0]:.1f})/{self.options[1]}({self.prob[1]:.1f}))"
        if self.prob[0] == 1.:
            detr = 0
        else:
            assert self.prob[1] == 1.
            detr = 1
        return f"{self.options[detr]}"

    @property
    def prob(self) -> tuple[float, float]:
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
            self.linked_selector: BinarySelector[tuple[Response, int]]\
                    = BinarySelector((
                        (my_response.options[0], next_state.options[0]), # Cooperate
                        (my_response.options[1], next_state.options[1]), # Betrayal
                    ), my_response.prob)

    def __str__(self):
        return f"{self.counterpart_response}-{self.my_response}->{self.next_state}"


    def response_state(self) -> tuple[Response, int]:
        if is_linked:
            return self.linked_selector.select()
        return self.my_response.select(), self.next_state.select()

    @classmethod
    def get_random_of(cls: Self, counterpart_response: Response, next_state_candidates: list[int]) -> Self:
        val_rand_response = random()
        val_rand_state = random()
        return cls.__init__(
            counterpart_response=counterpart_response, 
            my_response=BinarySelector(options=(Response.BETRAYAL, Response.COOPERATE), prob=(val_rand_response, 1 - val_rand_response)),
            is_linked=choice((True, False)),
            next_state=BinarySelector(options=sample(next_state_candidates, 2), prob=(val_rand_state, 1 - val_rand_state)),
            )


class DetrTransition(Transition):
    def __init__(self, counterpart_response: Response, my_response: Response, next_state: int):
        super().__init__(
            counterpart_response=counterpart_response,
            my_response=BinarySelector((my_response, my_response), (1, 0)),
            is_linked=True,
            next_state=BinarySelector((next_state, -1), (1, 0))
        )

    @classmethod
    def get_random_of(cls: Self, counterpart_response: Response, next_state_candidates: list[int]) -> Self:
        return cls(
            counterpart_response=counterpart_response,
            my_response=choice([Response.BETRAYAL, Response.COOPERATE]),
            next_state=choice(next_state_candidates),
        )

class Manager:
    def __init__(self):
        self._states: list[State] = []

    def __getitem__(self, key: int) -> State:
        if key < len(self):
            return self._states[key]
        elif key == len(self):
            self.add_state()
            return self._states[key]
        raise IndexError

    def __setitem__(self, key: int, value: State):
        raise NotImplementedError

    def __delitem__(self, key: int):
        del self._states[key]

    def __len__(self):
        return len(self._states)

    def __iter__(self):
        self._iter_idx: int = 0
        return self
    
    def __next__(self) -> State:
        if self._iter_idx < len(self):
            res = self._states[self._iter_idx]
            self._iter_idx += 1
            return res
        else:
            raise StopIteration

    def add_state(self):
        new_state = State(len(self), self)
        self._states.append(new_state)

    def get_state_candidates(self, initing_state: bool=False, has_new_state: bool=True) -> list[int]:
        max_num = len(self._states)
        if initing_state:
            max_num += 1
        if has_new_state:
            max_num += 1

        return list(range(max_num))

if __name__ == "__main__":
    # TODO: Make test code here
    manager = Manager()
    manager.add_state()
    for next_state in manager:
        print(next_state)
