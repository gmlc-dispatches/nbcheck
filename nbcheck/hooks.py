from typing import List
from typing import Optional
from typing import Union

import pytest

from nbcheck.api import Notebook


def pytest_nbcheck_info(config: pytest.Config) -> Optional[List[str]]:
    """
    Return a list of lines to be displayed at the beginning of the test run.
    """


def pytest_nbcollect_makeitem(collector: Notebook) -> Optional[Union[pytest.Collector, pytest.Item]]:
    """
    Create a :class:`pytest.Item` or :class:`pytest.Collector` from the passed :class:`Notebook` instance.
    """
