from pathlib import Path
from typing import List
from typing import Literal
from typing import Optional

import pytest
from _pytest.nodes import Node
from _pytest.pathlib import bestrelpath
import nbformat


Notebook = dict
Cell = dict
CellIndex = int


class Directory(Node):

    @classmethod
    def from_path(cls, path: Path, session: pytest.Session):
        relpath = bestrelpath(session.config.rootpath, path)

        return cls.from_parent(
            session,
            name=relpath,
            nodeid=relpath,
        )


class Notebook(pytest.Collector):

    @classmethod
    def from_path(cls,
            path: Path,
            session: pytest.Session,
            version: int = 4,
        ):
        nb = nbformat.read(path, version)

        parent = Directory.from_path(
            path.parent,
            session=session,
        )

        return cls.from_parent(
            parent,
            name=path.name,
            nb=nb,
            path=path,
            nodeid=bestrelpath(session.config.rootpath, path),
        )

    def __init__(self, *, nb: Notebook, path: Path, **kwargs):
        super().__init__(
            **kwargs,
        )
        self.path = path
        self.nb = nb

    def _cells(self, type_: str = Literal["code", "markdown"]) -> List[Cell]:
        return [
            c for c in self.nb.cells
            if c.cell_type == type_
        ]

    @property
    def code_cells(self) -> List[Cell]:
        return self._cells("code")

    @property
    def markdown_cells(self) -> List[Cell]:
        return self._cells("markdown")

    def collect(self):
        yield from self.ihook.pytest_nbcollect_makeitem(collector=self)
