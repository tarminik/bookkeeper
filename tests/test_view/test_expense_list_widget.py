"""
Tests for the ExpenseListWidget
"""

import pytest
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QTableWidgetItem, QMessageBox
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

from bookkeeper.view.expense_list_widget import ExpenseListWidget
from bookkeeper.models.expense import Expense
from bookkeeper.models.category import Category


@pytest.fixture
def widget(qapp):
    """Create ExpenseListWidget instance for tests"""
    widget = ExpenseListWidget()
    yield widget
    widget.deleteLater()


@pytest.fixture
def sample_expenses():
    """Create sample expenses for tests"""
    return [
        Expense(pk=1, amount=1000, category=1, expense_date=datetime(2025, 4, 1, 12, 0), comment="Lunch"),
        Expense(pk=2, amount=2500, category=2, expense_date=datetime(2025, 4, 1, 15, 30), comment="Groceries"),
        Expense(pk=3, amount=500, category=1, expense_date=datetime(2025, 4, 2, 9, 0), comment="Coffee")
    ]


@pytest.fixture
def sample_categories():
    """Create sample categories for tests"""
    return {
        1: Category(pk=1, name="Food", parent=None),
        2: Category(pk=2, name="Groceries", parent=None)
    }


def test_init(widget):
    """Test widget initialization"""
    assert widget.expenses == []
    assert widget.categories == {}
    assert widget.table.columnCount() == 5
    assert widget.table.horizontalHeaderItem(0).text() == "ID"
    assert widget.table.horizontalHeaderItem(1).text() == "Date"
    assert widget.table.horizontalHeaderItem(2).text() == "Category"
    assert widget.table.horizontalHeaderItem(3).text() == "Amount"
    assert widget.table.horizontalHeaderItem(4).text() == "Comment"


def test_set_expenses(widget, sample_expenses, sample_categories):
    """Test setting expenses"""
    widget.set_expenses(sample_expenses, sample_categories)
    
    assert widget.expenses == sample_expenses
    assert widget.categories == sample_categories
    assert widget.table.rowCount() == 3
    
    # Check first row
    assert widget.table.item(0, 0).text() == "1"
    assert widget.table.item(0, 1).text() == "2025-04-01 12:00"
    assert widget.table.item(0, 2).text() == "Food"
    assert widget.table.item(0, 3).text() == "10.00"
    assert widget.table.item(0, 4).text() == "Lunch"
    
    # Check second row
    assert widget.table.item(1, 0).text() == "2"
    assert widget.table.item(1, 1).text() == "2025-04-01 15:30"
    assert widget.table.item(1, 2).text() == "Groceries"
    assert widget.table.item(1, 3).text() == "25.00"
    assert widget.table.item(1, 4).text() == "Groceries"


def test_get_selected_expense_id(widget, sample_expenses, sample_categories):
    """Test getting selected expense ID"""
    widget.set_expenses(sample_expenses, sample_categories)
    
    # No selection
    assert widget.get_selected_expense_id() is None
    
    # Select first row
    widget.table.setCurrentCell(0, 0)
    assert widget.get_selected_expense_id() == 1
    
    # Select second row
    widget.table.setCurrentCell(1, 0)
    assert widget.get_selected_expense_id() == 2


def test_get_delete_confirmation(widget, monkeypatch):
    """Test delete confirmation dialog"""
    # Mock QMessageBox.question to return Yes
    monkeypatch.setattr(
        "PyQt5.QtWidgets.QMessageBox.question",
        lambda *args, **kwargs: QMessageBox.Yes
    )
    
    assert widget.get_delete_confirmation(1) is True
    
    # Mock QMessageBox.question to return No
    monkeypatch.setattr(
        "PyQt5.QtWidgets.QMessageBox.question",
        lambda *args, **kwargs: QMessageBox.No
    )
    
    assert widget.get_delete_confirmation(1) is False
