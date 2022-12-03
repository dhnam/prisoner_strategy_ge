import difflib
from typing import Callable, Sequence, Iterator
from itertools import chain


class Diffsxs(difflib.Differ):
    def __init__(self, linejunk: Callable[[str], bool] | None=None, charjunk: Callable[[str], bool]=None):
        super().__init__(linejunk, charjunk)
        self._maxlen: int = -1
        self._recent_indicator: str = ''
        self._recent_lines: list[str] = []
        #todo add things...

    def comparesbs(self, a: Sequence[str], b: Sequence[str], sep="") -> Iterator[str]:
        # Copy-pasted code from cpython difflib

        # First we need to know maximum length to make sbs compare pretty.
        self._maxlen = max(map(len, chain(a, b))) + 2

        cruncher = difflib.SequenceMatcher(self.linejunk, a, b)
        for tag, alo, ahi, blo, bhi in cruncher.get_opcodes():
            if tag == 'replace':
                g = self._fancy_replace(a, alo, ahi, b, blo, bhi)
            elif tag == 'delete':
                g = self._dump('-', a, alo, ahi)
            elif tag == 'insert':
                g = self._dump('+', b, blo, bhi)
            elif tag == 'equal':
                g = self._dump(' ', a, alo, ahi)
            else:
                raise ValueError('unknown tag %r' % (tag,))
            yield from self._build_sbs(g, sep=sep)

    def _build_sbs(self, lines: Iterator[str], sep='') -> Iterator[str]:
        def join_with_spaces(a: str, b: str, space: int, sep='') -> str:
            return ''.join([a.ljust(space), sep, b.ljust(space), "\n"])

        def new_line_start(*, a: str="", b: str="", a_replace: str | None=None, b_replace: str | None=None) -> Iterator[str]:
            yield join_with_spaces(a, b, self._maxlen, sep)
            if any([a_replace, b_replace]):
                yield join_with_spaces("" if a_replace is None else a_replace,
                                       "" if b_replace is None else b_replace,
                                        self._maxlen, sep)
        # new line patterns: " ", "-", "+", "-?+", "-+?", "-?+?"
        # tokens: " ", "-", "+", "?"
        for next_line in lines:
            next_line = next_line.strip("\n")
            self._recent_indicator += next_line[0]
            self._recent_lines.append(next_line)
            match self._recent_indicator:
                case " ":
                    yield from new_line_start(a=next_line, b=next_line)
                    self._recent_indicator = ''
                    self._recent_lines = []
                case "+":
                    yield from new_line_start(b=next_line)
                    self._recent_indicator = ''
                    self._recent_lines = []
                case "- ":
                    yield from new_line_start(a=self._recent_lines[0])
                    yield from new_line_start(a=next_line, b=next_line)
                    self._recent_indicator = ''
                    self._recent_lines = []
                case "--":
                    yield from new_line_start(a=self._recent_lines[0])
                    self._recent_indicator = "-"
                    self._recent_lines.pop(0)
                case "-+ ":
                    yield from new_line_start(a=self._recent_lines[0])
                    yield from new_line_start(b=self._recent_lines[1])
                    yield from new_line_start(a=next_line, b=next_line)
                    self._recent_indicator = ''
                    self._recent_lines = []
                case "-+-":
                    yield from new_line_start(a=self._recent_lines[0])
                    yield from new_line_start(b=self._recent_lines[1])
                    self._recent_indicator = '-'
                    self._recent_lines = self._recent_lines[2:]
                case "-++":
                    yield from new_line_start(a=self._recent_lines[0])
                    yield from new_line_start(b=self._recent_lines[1])
                    yield from new_line_start(b=next_line)
                    self._recent_indicator = ''
                    self._recent_lines = []
                case "-+?":
                    yield from new_line_start(a=self._recent_lines[0], b=self._recent_lines[1], b_replace=self._recent_lines[2])
                    self._recent_indicator = ''
                    self._recent_lines = []
                case "-? " | "-?-" | "-??":
                    raise Exception(self._recent_indicator)
                case "-?+ ":
                    yield from new_line_start(a=self._recent_lines[0], b=self._recent_lines[2], a_replace=self._recent_lines[1])
                    yield from new_line_start(a=next_line, b=next_line)
                    self._recent_indicator = ''
                    self._recent_lines = []
                case "-?+-":
                    yield from new_line_start(a=self._recent_lines[0], b=self._recent_lines[2], a_replace=self._recent_lines[1])
                    self._recent_indicator = '-'
                    self._recent_lines = self._recent_lines[3:]
                case "-?++":
                    yield from new_line_start(a=self._recent_lines[0], b=self._recent_lines[2], a_replace=self._recent_lines[1])
                    yield from new_line_start(b=next_line)
                    self._recent_indicator = ''
                    self._recent_lines = []
                case "-?+?":
                    yield from new_line_start(a=self._recent_lines[0], b=self._recent_lines[2], a_replace=self._recent_lines[1], b_replace=self._recent_lines[3])
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
    print(''.join(Diffsxs().comparesbs(a.splitlines(True),
                                        b.splitlines(True), sep="|")),
                    end="")