"""
Tests for the CategoryWidget
"""

import pytest
from PyQt5.QtWidgets import QApplication, QTreeWidgetItem, QMessageBox, QInputDialog
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

from bookkeeper.view.category_widget import CategoryWidget
from bookkeeper.models.category import Category


@pytest.fixture
def widget(qapp):
    """Create CategoryWidget instance for tests"""
    widget = CategoryWidget()
    yield widget
    widget.deleteLater()


@pytest.fixture
def sample_categories():
    """Create sample categories for tests"""
    return {
        1: Category(pk=1, name="Food", parent=None),
        2: Category(pk=2, name="Entertainment", parent=None),
        3: Category(pk=3, name="Fast Food", parent=1),
        4: Category(pk=4, name="Groceries", parent=1),
        5: Category(pk=5, name="Movies", parent=2)
    }


def test_init(widget):
    """Test widget initialization"""
    assert widget.categories == {}
    assert widget.tree is not None
    assert widget.add_button is not None
    assert widget.add_sub_button is not None
    assert widget.edit_button is not None
    assert widget.delete_button is not None


def test_set_categories(widget, sample_categories):
    """Test setting categories"""
    widget.set_categories(sample_categories)
    
    assert widget.categories == sample_categories
    
    # Check that root categories are added to tree
    assert widget.tree.topLevelItemCount() == 2
    
    # Check first root category
    root1 = widget.tree.topLevelItem(0)
    assert root1.text(0) == "Entertainment"
    assert root1.data(0, Qt.UserRole) == 2
    assert root1.childCount() == 1
    
    # Check subcategory of first root
    child1 = root1.child(0)
    assert child1.text(0) == "Movies"
    assert child1.data(0, Qt.UserRole) == 5
    
    # Check second root category
    root2 = widget.tree.topLevelItem(1)
    assert root2.text(0) == "Food"
    assert root2.data(0, Qt.UserRole) == 1
    assert root2.childCount() == 2
    
    # Check subcategories of second root
    child2_1 = root2.child(0)
    assert child2_1.text(0) == "Fast Food"
    assert child2_1.data(0, Qt.UserRole) == 3
    
    child2_2 = root2.child(1)
    assert child2_2.text(0) == "Groceries"
    assert child2_2.data(0, Qt.UserRole) == 4


def test_get_category_name(widget, monkeypatch):
    """Test getting category name"""
    # Mock QInputDialog.getText to return a name
    def mock_getText(*args, **kwargs):
        return "New Category", True
    
    monkeypatch.setattr("PyQt5.QtWidgets.QInputDialog.getText", mock_getText)
    
    name, ok = widget.get_category_name()
    assert name == "New Category"
    assert ok is True
    
    # Mock QInputDialog.getText to return cancel
    def mock_getText_cancel(*args, **kwargs):
        return "", False
    
    monkeypatch.setattr("PyQt5.QtWidgets.QInputDialog.getText", mock_getText_cancel)
    
    name, ok = widget.get_category_name()
    assert name == ""
    assert ok is False


def test_get_subcategory_info(widget, sample_categories, monkeypatch):
    """Test getting subcategory info"""
    widget.set_categories(sample_categories)
    
    # Mock QInputDialog.getText to return a name
    def mock_getText(*args, **kwargs):
        return "New Subcategory", True
    
    monkeypatch.setattr("PyQt5.QtWidgets.QInputDialog.getText", mock_getText)
    
    # Mock QMessageBox.warning for when no category is selected
    warning_shown = False
    
    def mock_warning(*args, **kwargs):
        nonlocal warning_shown
        warning_shown = True
        return QMessageBox.Ok
    
    monkeypatch.setattr("PyQt5.QtWidgets.QMessageBox.warning", mock_warning)
    
    # Try to get subcategory info with no selection
    parent_id, name, ok = widget.get_subcategory_info()
    assert parent_id is None
    assert name == ""
    assert ok is False
    assert warning_shown is True
    
    # Select a category and try again
    widget.tree.setCurrentItem(widget.tree.topLevelItem(1))  # Select "Food"
    parent_id, name, ok = widget.get_subcategory_info()
    assert parent_id == 1  # "Food" ID
    assert name == "New Subcategory"
    assert ok is True


def test_get_edit_info(widget, sample_categories, monkeypatch):
    """Test getting edit info"""
    widget.set_categories(sample_categories)
    
    # Mock QInputDialog.getText to return a new name
    def mock_getText(*args, **kwargs):
        return "Edited Category", True
    
    monkeypatch.setattr("PyQt5.QtWidgets.QInputDialog.getText", mock_getText)
    
    # Mock QMessageBox.warning for when no category is selected
    warning_shown = False
    
    def mock_warning(*args, **kwargs):
        nonlocal warning_shown
        warning_shown = True
        return QMessageBox.Ok
    
    monkeypatch.setattr("PyQt5.QtWidgets.QMessageBox.warning", mock_warning)
    
    # Try to get edit info with no selection
    category_id, name, ok = widget.get_edit_info()
    assert category_id is None
    assert name == ""
    assert ok is False
    assert warning_shown is True
    
    # Select a category and try again
    widget.tree.setCurrentItem(widget.tree.topLevelItem(1))  # Select "Food"
    category_id, name, ok = widget.get_edit_info()
    assert category_id == 1  # "Food" ID
    assert name == "Edited Category"
    assert ok is True


def test_get_delete_info(widget, sample_categories, monkeypatch):
    """Test getting delete info"""
    widget.set_categories(sample_categories)
    
    # Mock QMessageBox.question to return Yes
    def mock_question_yes(*args, **kwargs):
        return QMessageBox.Yes
    
    monkeypatch.setattr("PyQt5.QtWidgets.QMessageBox.question", mock_question_yes)
    
    # Mock QMessageBox.warning for when no category is selected
    warning_shown = False
    
    def mock_warning(*args, **kwargs):
        nonlocal warning_shown
        warning_shown = True
        return QMessageBox.Ok
    
    monkeypatch.setattr("PyQt5.QtWidgets.QMessageBox.warning", mock_warning)
    
    # Try to get delete info with no selection
    category_id, ok = widget.get_delete_info()
    assert category_id is None
    assert ok is False
    assert warning_shown is True
    
    # Select a category and try again
    widget.tree.setCurrentItem(widget.tree.topLevelItem(1))  # Select "Food"
    category_id, ok = widget.get_delete_info()
    assert category_id == 1  # "Food" ID
    assert ok is True
    
    # Mock QMessageBox.question to return No
    def mock_question_no(*args, **kwargs):
        return QMessageBox.No
    
    monkeypatch.setattr("PyQt5.QtWidgets.QMessageBox.question", mock_question_no)
    
    # Try again with No response
    category_id, ok = widget.get_delete_info()
    assert category_id == 1  # "Food" ID
    assert ok is False
