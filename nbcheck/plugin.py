from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from typing import List
from typing import Tuple

import pytest

from nbcheck.api import Notebook
from nbcheck.api import Directory


def pytest_addoption(parser: pytest.Parser):
    grp = parser.getgroup("nbcheck")
    grp.addoption(
        "--nbcheck",
        help="nbcheck checks category to enable. Can be given multiple times, e.g. `--nbcheck=static --nbcheck=exec`",
        action="append",
        default=None,
        dest="nbcheck",
        metavar="<category>",
    )
    grp.addoption(
        "--cell-timeout",
        help="Maximum time allowed for a cell to complete execution before raising an error, in seconds",
        action="store",
        # NOTE technically float, but <1 s doesn't really make sense
        type=int,
        default=600,
        dest="nbcheck_cell_timeout_s",
        metavar="<timeout in s>"
    )


def pytest_addhooks(pluginmanager: pytest.PytestPluginManager):
    from . import hooks

    pluginmanager.add_hookspecs(hooks)


def pytest_configure(config: pytest.Config):
    if config.option.nbcheck is None:
        return
    for cat in config.option.nbcheck:
        entry_point_group_name = f"nbcheck.{cat}"
        n_loaded = config.pluginmanager.load_setuptools_entrypoints(entry_point_group_name)
        if not n_loaded:
            raise ValueError(f"No entry_points plugins could be loaded for {entry_point_group_name!r}")


def pytest_ignore_collect(collection_path: Path):
    return ".ipynb_checkpoints" in collection_path.parts


@pytest.hookimpl(tryfirst=True)
def pytest_report_header(config: pytest.Config) -> List[str]:
    lines = []
    for name, plugin in config.pluginmanager.list_name_plugin():
        get_info = getattr(plugin, "pytest_nbcheck_info", None)
        if get_info is not None:
            lines.append(f"nbcheck: {name} ({plugin.__name__})")
            lines.extend([
                "\t" + line
                for line in get_info(config=config)
            ])
    return lines


def pytest_collect_file(file_path: Path, parent: pytest.Session):

    if file_path.suffix == ".ipynb":
        return Notebook.from_path(
            file_path,
            session=parent,
        )
