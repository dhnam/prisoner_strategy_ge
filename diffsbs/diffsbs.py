import difflib
from typing import Callable, Sequence, Iterator
from itertools import chain


class Diffsbs(difflib.Differ):
    def __init__(self, linejunk: Callable[[str], bool] | None=None, charjunk: Callable[[str], bool]=None):
        super().__init__(linejunk, charjunk)
        self._maxlen: int = -1
        #todo add things...

    def comparesbs(self, a: Sequence[str], b: Sequence[str]) -> Iterator[str]:
        # Copy-pasted code from cpython difflib

        # First we need to know maximum length to make sbs compare pretty.
        for next_len in map(len, chain(a, b)):
            if next_len > self._maxlen:
                self._maxlen = next_len

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
            g = self._build_sbs(tag, g, sep='')

            yield from g

    def _build_sbs(self, tag: str, lines: Iterator[str], sep='') -> Iterator[str]:
        def join_with_spaces(a: str, b: str, space: int, sep=''):
            return ''.join([a[:-1].ljust(space), sep, b[:-1].ljust(space), "\n"])
        a = ""
        a_replace = ""
        b = ""
        b_replace = ""
        was = ""
        replaced = False
        # print(list(lines))
        for next_line in lines:
            # print(next_line[:-1], a[:-1], b[:-1], a_replace[:-1], b_replace[:-1], sep=", ")
            if next_line[:2] == "- ":
                match was:
                    case "- ":
                        b = "\n"
                        yield join_with_spaces(a, b, self._maxlen, sep)
                        replaced = False
                    case "+ ":
                        a = "\n"
                        yield join_with_spaces(a, b, self._maxlen, sep)
                        replaced = False
                    case "? ":
                        yield join_with_spaces(a, b, self._maxlen, sep)
                        yield join_with_spaces(a_replace, b_replace, self._maxlen, sep)
                        replaced = False
                    case "  ":
                        yield join_with_spaces(a, b, self._maxlen, sep)
                        replaced = False
                a = next_line
                was = "- "
            if next_line[:2] == "+ ":
                match was:
                    case "- ":
                        b = "\n"
                        yield join_with_spaces(a, b, self._maxlen, sep)
                        replaced = False
                    case "+ ":
                        if replaced:
                            b_replace = "\n"
                            yield join_with_spaces(a, b, self._maxlen, sep)
                            yield join_with_spaces(a_replace, b_replace, self._maxlen, sep)
                            replaced = False
                        else:
                            a = "\n"
                            yield join_with_spaces(a, b, self._maxlen, sep)
                            replaced = False
                b = next_line
                was = "+ "
            if next_line[:2] == "? ":
                match was:
                    case "- ":
                        a_replace = next_line
                    case "+ ":
                        b_replace = next_line
                replaced = True
                was = "? "
            if next_line[:2] == "  ":
                match was:
                    case "- ":
                        b = "\n"
                        yield join_with_spaces(a, b, self._maxlen, sep)
                        replaced = False
                    case "+ ":
                        a = "\n"
                        yield join_with_spaces(a, b, self._maxlen, sep)
                        replaced = False
                    case "? ":
                        print("Haha sorry...")
                yield join_with_spaces(next_line, next_line, self._maxlen, sep)
                was = "  "
                replaced = False
        """ 
        match was:
                case "- ":
                case "+ ":
                case "? ":
                case "  ":
                case "":
                case _:
        """

        # TODO finish 'last token'

        """
        if tag == 'replace':
            
            a = next(lines)
            a_replace = next(lines)
            try:
                b = next(lines)
                b_replace = next(lines)
                yield join_with_spaces(a, b, self._maxlen, sep)
                yield join_with_spaces(a_replace, b_replace, self._maxlen, sep)
            except StopIteration:
                yield join_with_spaces(a, a_replace, self._maxlen, sep)
        elif tag == 'delete':
            a = next(lines)
            b = "\n"
            yield join_with_spaces(a, b, self._maxlen, sep)
        elif tag == 'insert':
            a = "\n"
            b = next(lines)
            yield join_with_spaces(a, b, self._maxlen, sep)
        elif tag == 'equal':
            a = next(lines)
            b = a
            yield join_with_spaces(a, b, self._maxlen, sep)
        else:
            raise ValueError('unknown tag %r' % (tag,))
        """


if __name__ == "__main__":
     print(''.join(Diffsbs().comparesbs('one\ntwo\nthree\nfour\nsix\n'.splitlines(True),
                                    'ore\ntree\nemu\nfour\nfive\n'.splitlines(True))),
                    end="")