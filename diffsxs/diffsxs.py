import difflib
from typing import Sequence, Iterator
from abc import ABC, abstractmethod

# TODO yak shaving for unicode characer && zero length character... how to calculate it && apply it in join_with_spaces

class SxsStratagy(ABC):
    def __init__(self, sep=""):
        self.maxlen = -1
        self.sep = sep
    
    def join_with_spaces(self, a: str, b: str) -> str:
        return f"{a:<{self.maxlen}}{self.sep}{b:<{self.maxlen}}" + "\n"

    @abstractmethod
    def next_line(self, *, a: str="", b: str="", a_replace: str | None=None, b_replace: str | None=None) -> Iterator[str]:
        pass

class SimpleSxsStratagy(SxsStratagy):
    def next_line(self, *, a: str="", b: str="", a_replace: str | None=None, b_replace: str | None=None) -> Iterator[str]:
        yield self.join_with_spaces(a, b)
        if any([a_replace, b_replace]):
            yield self.join_with_spaces(
                "" if a_replace is None else a_replace,
                "" if b_replace is None else b_replace,
                )


class UnicodeOnelineSxsStratagy(SxsStratagy):
    def next_line(self, *, a: str = "", b: str = "", a_replace: str | None = None, b_replace: str | None = None) -> Iterator[str]:
        strike_char = "\N{COMBINING LONG STROKE OVERLAY}"
        underline_char = "\N{COMBINING LOW LINE}"
        def combine_str(string, char, place:list[bool] = None):
            combined: str = ""
            if place is None:
                place = [True] * len(string)
            assert len(place) == len(string)
            for next_char, is_combined in zip(string, place):
                combined += next_char
                if is_combined:
                    combined += char
            return combined

        processed: list[str] = ["", ""]
        for i, (string, cue) in enumerate([(a, a_replace), (b, b_replace)]):
            if string == "":
                processed[i] = ""
                continue
            line_cue, string = string[:2], string[2:]
            cue_place = [False] * len(string)
            if cue is None:
                cue_place = [True] * len(string)
            else:
                cue = cue[2:]
                for j, next_char in enumerate(cue):
                    cue_place[j] = (next_char != " ")
            match line_cue:
                case "  ":
                    processed[i] = string
                case "- ":
                    processed[i] = combine_str(string, strike_char, cue_place)
                case "+ ":
                    processed[i] = combine_str(string, underline_char, cue_place)
        yield self.join_with_spaces(*processed)


        


class Diffsxs:
    def __init__(self, sxs_stratagy: SxsStratagy | None=None):
        self._recent_indicator: str = ''
        self._recent_lines: list[str] = []
        if sxs_stratagy is None:
            sxs_stratagy = SimpleSxsStratagy()
        self.sxs_stratagy = sxs_stratagy

    def comparesbs(self, a: Sequence[str], b: Sequence[str]) -> Iterator[str]:
        self.sxs_stratagy.maxlen = max(map(len, a)) + 2
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
    b = """Fierstly
thiid
forth
fivth
sixth
seventh"""
    print(''.join(difflib.Differ().compare(a.splitlines(True),
                                        b.splitlines(True))),
                    end="")
    print()
    sxs_stratagy = UnicodeOnelineSxsStratagy(sep="|")
    print(''.join(Diffsxs(sxs_stratagy=sxs_stratagy).comparesbs(a.splitlines(True),
                                                                b.splitlines(True))),
                    end="")