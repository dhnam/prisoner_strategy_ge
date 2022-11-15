from __future__ import annotations
from enum import Enum, auto
from typing import TypeVar, Generic, Self
from random import choices, choice, random, sample
from textwrap import indent
from dataclasses import dataclass
from abc import ABC, abstractmethod
from basic_config import *

# Classes: Strategy / State / Transition / Manager

TransitionType = TypeVar('TransitionType', bound='Transition')

class Clonable(ABC):
    @classmethod
    @abstractmethod
    def clone(cls, src: Self) -> Self:
        pass


class Strategy(Clonable):
    def __init__(self, name: str):
        self.name = name
        self.manager = Manager()
        self.manager.add_state()
        self.curr_state: int = 0
        if random() < RANDOM_DETR_STATE_RATIO:
            coop_prob = random()
            self.first_move: BinarySelector[Response] = BinarySelector((Response.COOPERATE, Response.BETRAYAL), (coop_prob, 1 - coop_prob))
        else:
            response = choice((Response.COOPERATE, Response.BETRAYAL))
            self.first_move: BinarySelector[Response] = BinarySelector((response, response), (1, 0))

    def __str__(self):
        ret_str = f"Stratage {self.name}\n"
        ret_str += "{\n"
        ret_str += f"\tFirst move: {self.first_move}\n"
        for i, next_state in enumerate(self.manager):
            ret_str += indent(str(next_state), "\t")
            ret_str += "\n"
        ret_str += "\n}"
        return ret_str

    def make_first_move(self):
        return self.first_move.select()
    
    def make_response(self, counterpart_response: Response) -> Response:
        res, next_state = self.manager[self.curr_state].response_state(counterpart_response)
        self.curr_state = next_state
        return res
    
    def reset(self):
        self.curr_state = 0

    @classmethod
    def clone(cls, src: Self) -> Self:
        new = cls.__new__(cls)
        new.name = src.name
        new.manager = Manager.from_state_list(list(map(State.clone, src.manager)))
        new.curr_state = 0
        new.first_move = BinarySelector.clone(src.first_move)
        return new

    def mutate(self, prob: float) -> Self:
        if random() < prob:
            if random() < RANDOM_DETR_STATE_RATIO:
                coop_prob = random()
                self.first_move: BinarySelector[Response] = BinarySelector((Response.COOPERATE, Response.BETRAYAL), (coop_prob, 1 - coop_prob))
            else:
                response = choice((Response.COOPERATE, Response.BETRAYAL))
                self.first_move: BinarySelector[Response] = BinarySelector((response, response), (1, 0))
        for next_state in self.manager:
            for next_response in Response:
                if random() < prob:
                    next_state.point_mutate_transition(next_response)
        return self



class State(Clonable):
    def __init__(self, state_num: int, manager: Manager):
        self.state_num = state_num
        self.manager = manager
        self.state_transitions: dict[Response, TransitionType] = {}
        for next_response in Response:
            self.point_mutate_transition(next_response)

    def __str__(self):
        ret_str = f"State {self.state_num}\n"
        ret_str += "{\n"
        for next_response in Response:
            ret_str += f"\t{self.state_transitions[next_response]}\n"
        ret_str += "}"
        return ret_str

    def point_mutate_transition(self, response: Response):
        state_candidates = self.manager.get_state_candidates()
        transition_type: type[TransitionType] = Transition
        if random() > RANDOM_DETR_STATE_RATIO:
            transition_type = DetrTransition
        self.state_transitions[response] = transition_type.get_random_of(response, state_candidates)
        tracked_candidates = self.manager.get_state_candidates(has_new_state=False)
        for next_option in self.state_transitions[response].next_state.options:
            if next_option >= 0 and next_option not in tracked_candidates:
                self.manager[next_option] # Calling __getitem__ to initialize new state

    def response_state(self, counterpart_response: Response) -> tuple[Response, int]:
        return self.state_transitions[counterpart_response].response_state()

    @classmethod
    def clone(cls, src: Self) -> Self:
        new = cls.__new__(cls)
        new.state_num = src.state_num
        new.manager = src.manager
        new.state_transitions = {res: type(trn).clone(trn) for res, trn in src.state_transitions.items()}
        return new


class Response(Enum):
    COOPERATE = auto()
    BETRAYAL = auto()
    def __str__(self):
        if self.name == 'BETRAYAL':
            return "B"
        if self.name == "COOPERATE":
            return "C"
        raise TypeError

    def __repr__(self):
        return str(self)

T = TypeVar('T')

class BinarySelector(Generic[T], Clonable):
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

    def select(self) -> T:
        return choices(self.options, weights=self._prob)[0]

    @classmethod
    def clone(cls, src: Self) -> Self:
        return cls(src.options, src.prob)
    
    

class Transition(Clonable):
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
        if self.is_linked:
            return self.linked_selector.select()
        return self.my_response.select(), self.next_state.select()

    @classmethod
    def get_random_of(cls: Self, counterpart_response: Response, next_state_candidates: list[int]) -> Self:
        val_rand_response = random()
        val_rand_state = random()
        return cls(
            counterpart_response=counterpart_response, 
            my_response=BinarySelector(options=(Response.BETRAYAL, Response.COOPERATE), prob=(val_rand_response, 1 - val_rand_response)),
            is_linked=choice((True, False)),
            next_state=BinarySelector(options=sample(next_state_candidates, 2), prob=(val_rand_state, 1 - val_rand_state)),
            )
    
    @classmethod
    def clone(cls, src: Self) -> Self:
        new = cls.__new__(cls)
        new.counterpart_response = src.counterpart_response
        new.my_response = src.my_response
        new.is_linked = src.is_linked
        new.next_state = src.next_state
        if new.is_linked:
            new.linked_selector: BinarySelector[tuple[Response, int]]\
                    = BinarySelector((
                        (new.my_response.options[0], new.next_state.options[0]), # Cooperate
                        (new.my_response.options[1], new.next_state.options[1]), # Betrayal
                    ), new.my_response.prob)
        return new



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
        self._states: list[State | None] = []

    def __getitem__(self, key: int) -> State:
        if key < len(self):
            return self._states[key]
        elif key == len(self):
            self.add_state()
            return self._states[key]
        raise IndexError(f"len:{len(self)}, key:{key}")

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
        idx = len(self._states)
        self._states.append(None)
        self._states[idx] = State(len(self) - 1, self)

    def get_state_candidates(self, has_new_state: bool=True) -> list[int]:
        max_num = len(self._states)
        if has_new_state:
            max_num += 1

        return list(range(max_num))

    @classmethod
    def from_state_list(cls, state_list: list[State]):
        new = cls.__new__(cls)
        state_list = sorted(state_list, key=lambda x: x.state_num)
        new._states = state_list
        for next_state in state_list:
            next_state.manager = new
        return new

if __name__ == "__main__":
    from duel import Duel
    # TODO: Make test code here
    stratage1 = Strategy("test1")
    print(stratage1)
    stratage2 = Strategy.clone(stratage1).mutate(MUTATE_RATE)
    stratage2.name = "test2"
    print(stratage2)
    for i, (next_response, next_reward) in enumerate(Duel(stratage1, stratage2, REWARD_TABLE, 10)):
        print(f"{i}: {next_response}, {next_reward}")
