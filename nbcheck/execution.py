from contextlib import contextmanager
import os
from pathlib import Path
import shutil
import sys
from typing import List

import pytest
from ipykernel import kernelspec
from nbval import plugin as nbval_plugin
from nbcheck.api import Notebook


kernel_name = pytest.StashKey[str]()
kernelspec_path = pytest.StashKey[Path]()
current_pid = pytest.StashKey[int]()


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
    pid = os.getpid()
    kname = f"nbcheck-kernel-{pid}"
    config.pluginmanager.unregister(nbval_plugin)

    opt = config.option

    opt.nbval_lax = True
    opt.nbval_current_env = False
    opt.nbval_kernel_name = kname

    config.stash[current_pid] = pid
    config.stash[kernel_name] = kname


def pytest_nbcheck_info(config: pytest.Config) -> List[str]:
    kname = config.stash[kernel_name]
    lines = [
        f"Notebooks will be executed using kernel: {kname!r}",
        "It will be removed at the end of the run.",
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
    stash = session.config.stash
    kname = stash[kernel_name]

    with temp_kernelspec(kname) as kpath:
        stash[kernelspec_path] = kpath
        yield
