from collections import defaultdict
from pathlib import Path
import re
from typing import (
    Any,
    Callable,
    Iterable,
    List,
    Mapping,
    Union,
)

import pytest
import nbformat

from _pytest.python import Metafunc
from _pytest.terminal import TerminalReporter
from _pytest.reports import TestReport
from _pytest.config import Config
# from _pytest.stash import Stash, StashKey


def _get_nb_paths(search_root_dir: Path) -> List[Path]:
    search_root_dir = search_root_dir.resolve()
    assert search_root_dir.is_dir()
    return sorted(
        p.relative_to(search_root_dir)
        for p in search_root_dir.rglob("*.ipynb")
        if (
            not ".ipynb_checkpoints" in p.parts
        )
    )


_MAP_OUTCOME_TO_EMOJI = {
    "failed": "❌",
    "passed": "✅",
    "skipped": "⏭️",
}


class NBCheck:

    def __init__(self, nb_paths: Iterable[Path]):
        self._nb_paths = list(nb_paths)
        self._current_nb: Union[Path, None] = None
        self._reports_by_nb: Mapping[Path, TestReport] = defaultdict(list)
        self._report_types_to_collect = frozenset({"call"})

    def pytest_generate_tests(self, metafunc: Metafunc):
        if "nb_path" in metafunc.fixturenames:
            metafunc.parametrize("nb_path", self._nb_paths, ids=str, scope="class")

    @pytest.fixture(scope="class")
    def nb_node(self, nb_path: Path, request) -> nbformat.NotebookNode:
        self._current_nb = nb_path
        return nbformat.read(nb_path, as_version=4)

    def pytest_report_teststatus(self, report: TestReport, config: Config):
        should_collect = (
            report.when in self._report_types_to_collect
            and self._current_nb is not None
        )
        if should_collect:
            self._reports_by_nb[self._current_nb].append(report)

    def _get_test_outcome_summary(self, report: TestReport) -> str:
        return _MAP_OUTCOME_TO_EMOJI[report.outcome]

    def _get_test_location_summary(self, report: TestReport) -> str:
        test_repr = report.location[-1]
        test_repr = re.sub(
            # remove square brackets at the end and anything between them
            pattern=r"\[.+\]$",
            repl="",
            string=test_repr,
        )
        return test_repr

    def pytest_terminal_summary(self, terminalreporter: TerminalReporter):
        if not self._reports_by_nb:
            return
        tr = terminalreporter
        tr.section("Jupyter notebooks")
        for nb_path, reps in self._reports_by_nb.items():
            tr.section(nb_path.name)
            tr.ensure_newline()
            tr.write_line(f"Path: {str(nb_path)}")
            tr.ensure_newline()
            tr.write_line("Test outcomes:")
            tr.ensure_newline()
            for rep in reps: 
                outcome_summary = self._get_test_outcome_summary(rep)
                test_loc_summary = self._get_test_location_summary(rep)
                tr.write_line(f"{outcome_summary}\t{test_loc_summary}")


plugin = NBCheck(
    nb_paths=_get_nb_paths(search_root_dir=Path("."))
)
