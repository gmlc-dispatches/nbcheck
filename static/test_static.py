from dataclasses import dataclass
import re
from typing import (
    Dict,
    Iterable,
    List,
    Optional,
)

import pytest


class TestCellExecution:
    CodeCell = Dict
    CodeCells = List[CodeCell]
    CellIndexes = List[int]

    @pytest.fixture
    def nonempty_code_cells(self, nb_node) -> CodeCells:
        return [
            cell
            for cell in nb_node.cells
            if cell.cell_type == "code"
            and bool(cell.source)
        ]

    @pytest.fixture
    def cell_exe_indexes(self, nonempty_code_cells, replace_none_with: int = 0) -> CellIndexes:
        # WHY we replace instances of None with 0 (i.e. a false-y number)
        # to facilitate assertions involving sorting
        return [
            cell.execution_count or replace_none_with
            for cell in nonempty_code_cells
        ]

    @pytest.fixture
    def cell_exe_indexes_expected(self, nonempty_code_cells, offset_from_zero_based: int = 1) -> CellIndexes:
        return list(range(offset_from_zero_based, len(nonempty_code_cells) + offset_from_zero_based))
        
    def test_any_cell_executed(self, cell_exe_indexes):
        assert any([bool(idx) for idx in cell_exe_indexes])

    def test_all_cells_executed(self, cell_exe_indexes):
        assert [bool(idx) for idx in cell_exe_indexes] == [True] * len(cell_exe_indexes)

    def test_cells_executed_in_definition_order(self, cell_exe_indexes):
        assert cell_exe_indexes == sorted(cell_exe_indexes)

    def test_cells_executed_in_definition_order_without_gaps(self, cell_exe_indexes, cell_exe_indexes_expected):
        assert cell_exe_indexes == cell_exe_indexes_expected


@dataclass
class Header:
    level: int
    text: str

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


class TestHeaderStructure:

    @pytest.fixture
    def markdown_cells(self, nb_node):
        return [
            cell for cell in nb_node.cells
            if cell.cell_type == "markdown"
        ]

    @pytest.fixture
    def markdown_headers(self, markdown_cells):
        headers = []
        for cell in markdown_cells:
            lines = cell.source.split("\n")
            headers.extend(Header.from_lines(lines))
        return headers

    def test_headers_are_present(self, markdown_headers):
        assert len(markdown_headers) > 0

    @pytest.fixture
    def first_header(self, markdown_headers):
        return markdown_headers[0]

    @pytest.fixture
    def other_headers(self, markdown_headers):
        return markdown_headers[1:]

    def test_first_header_is_level_1(self, first_header):
        assert first_header.level == 1

    def test_other_headers_are_not_level_1(self, other_headers):
        for header in other_headers:
            assert header.level > 1
