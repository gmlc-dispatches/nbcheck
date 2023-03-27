from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from typing import List
from typing import Tuple

import pytest

from nbcheck.api import Notebook
from nbcheck.api import Directory


def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "--nbcheck",
        action="store_true",
        default=None,
        dest="nbcheck",
    )


def pytest_addhooks(pluginmanager: pytest.PytestPluginManager):
    from . import hooks

    pluginmanager.add_hookspecs(hooks)


def pytest_configure(config: pytest.Config):
    if config.option.nbcheck:
        config.pluginmanager.load_setuptools_entrypoints("nbcheck")


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
