from contextlib import contextmanager
from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import sys
from typing import List

import pytest
from ipykernel import kernelspec
from nbval import plugin as nbval_plugin
from nbcheck.api import Notebook


@dataclass
class Settings:
    kernel_name: str = ""
    kernelspec_path: Path = None
    current_pid: int = os.getpid()
    cell_timeout_s: int = -1


settings = pytest.StashKey[Settings]()


@contextmanager
def temp_kernelspec(name: str, **kwargs) -> Path:
    kspec_path = kernelspec.install(
        kernel_name=name,
        user=True,
        # prefix=sys.prefix,
        **kwargs
    )
    try:
        yield kspec_path
    finally:
        shutil.rmtree(kspec_path)


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config):

    s = config.stash[settings] = Settings()
    opt = config.option

    opt.nbval_lax = True
    opt.nbval_current_env = False
    opt.nbval_kernel_name = s.kernel_name = f"nbcheck-kernel-{s.current_pid}"
    opt.nbval_cell_timeout = s.cell_timeout_s = int(opt.nbcheck_cell_timeout_s)

    config.pluginmanager.unregister(nbval_plugin)


def pytest_nbcheck_info(config: pytest.Config) -> List[str]:
    s = config.stash[settings]
    lines = [
        f"Notebooks will be executed using kernel: {s.kernel_name!r}",
        "It will be removed at the end of the run.",
    ]
    lines += [
        f"Cell timeout set to {s.cell_timeout_s} s."
    ]
    return lines


@pytest.hookimpl(trylast=True)
def pytest_nbcollect_makeitem(collector: Notebook):
    return nbval_plugin.IPyNbFile.from_parent(
        parent=collector,
        path=collector.path,
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtestloop(session: pytest.Session):
    s = session.config.stash[settings]

    with temp_kernelspec(s.kernel_name) as kpath:
        s.kernelspec_path = kpath
        yield
