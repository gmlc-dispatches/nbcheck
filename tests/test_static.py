from typing import (
    Dict,
    List,
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
