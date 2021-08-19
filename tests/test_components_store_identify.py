import importlib.resources
import logging
from pathlib import Path

import pytest

from leaf_focus.components.store.identify import Identify


class TestComponentsStoreIdentify:
    def test_path_not_found(self):
        path = "this-path-does-not-exist"
        with pytest.raises(
            FileNotFoundError,
            match=f"Path does not exist '{path}'.",
        ):
            identify = Identify(logging.getLogger())
            identify.file_hash(Path(path))

    def test_file_hash(self):
        package = "tests.resources"
        name = "generic-data-file.txt"
        expected = "2d6f1f7a2558f6415e120453356a62ccbc6b27a66d0ef1253eb6610f5f679cc7"
        with importlib.resources.path(package, name) as path:
            identify = Identify(logging.getLogger())
            actual = identify.file_hash(path)
            assert actual == expected
