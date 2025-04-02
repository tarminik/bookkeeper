"""
Common fixtures for GUI tests
"""

import pytest
from PyQt5.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """Create a QApplication instance that will be used for all tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
