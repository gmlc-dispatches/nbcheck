from dataclasses import dataclass
import re
from typing import Iterable
from typing import List
from typing import Optional

import pytest

from nbcheck.api import Notebook
from nbcheck.api import CellIndex


@dataclass
class Header:
    level: int
    text: str
    cell_index: Optional[CellIndex] = None

    @classmethod
    def from_text(
            cls,
            text: str,
            pattern: Optional[re.Pattern] = re.compile(r"(?P<prefix>^[#]{1,6}) (?P<text>.+)$")
        ):
        match = re.match(pattern, text)
        if not match:
            return None
        return cls(
            level=len(match["prefix"]),
            text=match["text"],
        )

    @classmethod
    def from_lines(
            cls,
            lines: Iterable[str],
            **kwargs,
        ):
        for line in lines:
            # print(line)
            h = cls.from_text(line, **kwargs)
            # print(h)
            if h:
                yield h


class Headers:

    @classmethod
    def from_markdown_cells(cls, cells: Iterable, **kwargs):
        headers = []
        for cell in cells:
            lines = cell.source.split("\n")
            headers.extend(Header.from_lines(lines))
        return cls(headers, **kwargs)

    def __init__(self, headers):
        self._headers = headers

    def __iter__(self):
        return iter(self._headers)

    def __len__(self) -> int:
        return len(self._headers)

    @property
    def first(self) -> Header:
        return self._headers[0]

    @property
    def after_first(self) -> List[Header]:
        return self._headers[1:]

    def level(self, level: int):
        return [
            h for h in self
            if h.level == level
        ]


@dataclass
class InvalidMarkdownStructure(Exception):
    expected: str
    instead: str


class MissingHeader(InvalidMarkdownStructure): pass


class HeaderStructure(pytest.Item):

    def __init__(self, *, headers: Headers, **kwargs):
        super().__init__(**kwargs)
        self.headers = headers

    def runtest(self):
        if not self.headers:
            raise InvalidMarkdownStructure(
                expected="There should be at least one Markdown header",
                instead="No headers found"
            )
        if self.headers.first.level > 1:
            raise InvalidMarkdownStructure(
                expected="The first header should be a Level 1 header",
                instead=f"First header: {self.headers.first}"
            )
        level_ones = self.headers.level(1)
        if level_ones != [self.headers.first]:
            raise InvalidMarkdownStructure(
                expected="There should be only one Level 1 header",
                instead="\n".join([str(h) for h in level_ones])
            )

    def repr_failure(self, excinfo):
        exc = excinfo.value
        if isinstance(exc, InvalidMarkdownStructure):
            return f"expected: {exc.expected}\ninstead found: {exc.instead}"
        return repr(exc)

    def reportinfo(self):
        return self.parent.path, None, f"{self.parent.name} {self.name}"


def pytest_nbcollect_makeitem(collector: Notebook):
    headers = Headers.from_markdown_cells(collector.markdown_cells)
    return HeaderStructure.from_parent(
        collector,
        name=f"headers ({len(headers)})",
        headers=headers,
    )


def pytest_nbcheck_info(config: pytest.Config):
    return []