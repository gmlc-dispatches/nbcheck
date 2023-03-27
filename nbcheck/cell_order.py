from typing import Dict
from typing import Iterable

import pytest

from nbcheck.api import Notebook
from nbcheck.api import Cell
from nbcheck.api import CellIndex


class CellExecutionError(Exception): pass


class NotExecuted(CellExecutionError): pass


class OutOfOrder(CellExecutionError): pass



class CellIndexCheck(pytest.Item):

    @classmethod
    def from_code_cells(cls, code_cells: Iterable[Cell], parent: pytest.Collector):
        for expected_index, cell in enumerate(code_cells, start=1):
            name = f"[{expected_index}]"
            yield cls.from_parent(
                parent=parent,
                name=name,
                cell=cell,
                expected=expected_index,
            )

    def __init__(self, *, cell: Cell, expected: CellIndex, **kwargs):
        super().__init__(**kwargs)
        self.cell = cell
        self.expected = expected

    @property
    def actual(self) -> CellIndex:
        return self.cell.execution_count

    def runtest(self):
        if self.expected is None:
            raise NotExecuted()

        if self.cell.execution_count != self.expected:
            raise OutOfOrder()

    def repr_failure(self, excinfo):
        exc = excinfo.value
        if isinstance(exc, NotExecuted):
            return "Cell not executed!"
        if isinstance(exc, OutOfOrder):
            return "\n".join([
                "Cell was executed out of order", 
                f"\texpected index: {self.expected}",
                f"\tactual index: {self.actual}",
            ])
        return repr(exc)


class CellOrder(pytest.Collector):
    def __init__(self, *, cells, name=None, **kwargs):
        self.cells = list(cells)
        name = name or f"1-{len(self.cells)}"
        super().__init__(name=name, **kwargs)

    def collect(self):
        for expected_index, cell in enumerate(self.cells, start=1):
            name = f"[{expected_index}]"
            yield CellIndexCheck.from_parent(
                parent=self,
                name=name,
                cell=cell,
                expected=expected_index,
            )


def pytest_nbcollect_makeitem(collector: Notebook):
    cells = collector.code_cells
    return CellOrder.from_parent(
        parent=collector,
        cells=cells,
        name=f"(code) 1-{len(cells)}"
    )


def pytest_nbcheck_info(config: pytest.Config):
    return []