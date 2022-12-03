import difflib
from typing import Sequence, Iterator
from itertools import chain
from abc import ABC, abstractmethod

class SxsStratagy(ABC):
    def __init__(self):
        self.maxlen = -1
    
    @abstractmethod
    def next_line(self, *, a: str="", b: str="", a_replace: str | None=None, b_replace: str | None=None) -> Iterator[str]:
        pass

class SimpleSxsStratagy(SxsStratagy):
    def __init__(self, sep=""):
        super().__init__()
        self.sep = sep

    def next_line(self, *, a: str="", b: str="", a_replace: str | None=None, b_replace: str | None=None) -> Iterator[str]:

        def join_with_spaces(a: str, b: str, space: int, sep='') -> str:
            return ''.join([a.ljust(space), sep, b.ljust(space), "\n"])

        yield join_with_spaces(a, b, self.maxlen, self.sep)
        if any([a_replace, b_replace]):
            yield join_with_spaces("" if a_replace is None else a_replace,
                                    "" if b_replace is None else b_replace,
                                    self.maxlen, self.sep)

class Diffsxs:
    def __init__(self, sxs_stratagy: SxsStratagy | None=None):
        self._recent_indicator: str = ''
        self._recent_lines: list[str] = []
        if sxs_stratagy is None:
            sxs_stratagy = SimpleSxsStratagy()
        self.sxs_stratagy = sxs_stratagy

    def comparesbs(self, a: Sequence[str], b: Sequence[str]) -> Iterator[str]:
        self.sxs_stratagy.maxlen = max(map(len, chain(a, b))) + 2
        lines = difflib.Differ().compare(a, b)
        # new line patterns: " ", "-", "+", "-?+", "-+?", "-?+?"
        # tokens: " ", "-", "+", "?"
        for next_line in lines:
            next_line = next_line.strip("\n")
            self._recent_indicator += next_line[0]
            self._recent_lines.append(next_line)
            match self._recent_indicator:
                case " ":
                    yield from self.sxs_stratagy.next_line(a=next_line, b=next_line)
                    self._recent_indicator = ''
                    self._recent_lines = []
                case "+":
                    yield from self.sxs_stratagy.next_line(b=next_line)
                    self._recent_indicator = ''
                    self._recent_lines = []
                case "- ":
                    yield from self.sxs_stratagy.next_line(a=self._recent_lines[0])
                    yield from self.sxs_stratagy.next_line(a=next_line, b=next_line)
                    self._recent_indicator = ''
                    self._recent_lines = []
                case "--":
                    yield from self.sxs_stratagy.next_line(a=self._recent_lines[0])
                    self._recent_indicator = "-"
                    self._recent_lines.pop(0)
                case "-+ ":
                    yield from self.sxs_stratagy.next_line(a=self._recent_lines[0])
                    yield from self.sxs_stratagy.next_line(b=self._recent_lines[1])
                    yield from self.sxs_stratagy.next_line(a=next_line, b=next_line)
                    self._recent_indicator = ''
                    self._recent_lines = []
                case "-+-":
                    yield from self.sxs_stratagy.next_line(a=self._recent_lines[0])
                    yield from self.sxs_stratagy.next_line(b=self._recent_lines[1])
                    self._recent_indicator = '-'
                    self._recent_lines = self._recent_lines[2:]
                case "-++":
                    yield from self.sxs_stratagy.next_line(a=self._recent_lines[0])
                    yield from self.sxs_stratagy.next_line(b=self._recent_lines[1])
                    yield from self.sxs_stratagy.next_line(b=next_line)
                    self._recent_indicator = ''
                    self._recent_lines = []
                case "-+?":
                    yield from self.sxs_stratagy.next_line(a=self._recent_lines[0], b=self._recent_lines[1], b_replace=self._recent_lines[2])
                    self._recent_indicator = ''
                    self._recent_lines = []
                case "-? " | "-?-" | "-??":
                    raise Exception(self._recent_indicator)
                case "-?+ ":
                    yield from self.sxs_stratagy.next_line(a=self._recent_lines[0], b=self._recent_lines[2], a_replace=self._recent_lines[1])
                    yield from self.sxs_stratagy.next_line(a=next_line, b=next_line)
                    self._recent_indicator = ''
                    self._recent_lines = []
                case "-?+-":
                    yield from self.sxs_stratagy.next_line(a=self._recent_lines[0], b=self._recent_lines[2], a_replace=self._recent_lines[1])
                    self._recent_indicator = '-'
                    self._recent_lines = self._recent_lines[3:]
                case "-?++":
                    yield from self.sxs_stratagy.next_line(a=self._recent_lines[0], b=self._recent_lines[2], a_replace=self._recent_lines[1])
                    yield from self.sxs_stratagy.next_line(b=next_line)
                    self._recent_indicator = ''
                    self._recent_lines = []
                case "-?+?":
                    yield from self.sxs_stratagy.next_line(a=self._recent_lines[0], b=self._recent_lines[2], a_replace=self._recent_lines[1], b_replace=self._recent_lines[3])
                    self._recent_indicator = ''
                    self._recent_lines = []
        
if __name__ == "__main__":
    a = """First
second
third
fourth
fifth
seventh"""
    b = """Firstly
thiid
forth
fivth
sixth
seventh"""
    print(''.join(difflib.Differ().compare(a.splitlines(True),
                                        b.splitlines(True))),
                    end="")
    print()
    sxs_stratagy = SimpleSxsStratagy(sep="|")
    print(''.join(Diffsxs(sxs_stratagy=sxs_stratagy).comparesbs(a.splitlines(True),
                                                                b.splitlines(True))),
                    end="")