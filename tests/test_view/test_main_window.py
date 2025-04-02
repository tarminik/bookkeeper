"""
Tests for the MainWindow
"""

import pytest
from PyQt5.QtWidgets import QApplication, QTabWidget
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

from bookkeeper.view.main_window import MainWindow, CategoryDialog
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.models.budget import Budget
from datetime import datetime


@pytest.fixture
def window(qapp):
    """Create MainWindow instance for tests"""
    window = MainWindow()
    yield window
    window.deleteLater()


@pytest.fixture
def sample_categories():
    """Create sample categories for tests"""
    return {
        1: Category(pk=1, name="Food", parent=None),
        2: Category(pk=2, name="Entertainment", parent=None),
        3: Category(pk=3, name="Fast Food", parent=1)
    }


@pytest.fixture
def sample_expenses():
    """Create sample expenses for tests"""
    return [
        Expense(pk=1, amount=1000, category=1, expense_date=datetime(2025, 4, 1, 12, 0), comment="Lunch"),
        Expense(pk=2, amount=2500, category=2, expense_date=datetime(2025, 4, 1, 15, 30), comment="Movie"),
        Expense(pk=3, amount=500, category=3, expense_date=datetime(2025, 4, 2, 9, 0), comment="Coffee")
    ]


def test_init(window):
    """Test window initialization"""
    assert window.windowTitle() == "Bookkeeper - Personal Finance Manager"
    assert window.tabs is not None
    assert window.tabs.count() == 3
    assert window.tabs.tabText(0) == "Expenses"
    assert window.tabs.tabText(1) == "Budget"
    assert window.tabs.tabText(2) == "Add Expense"
    
    assert window.expense_list is not None
    assert window.budget_widget is not None
    assert window.add_expense_widget is not None
    assert window.categories_button is not None
    assert window.refresh_button is not None
    assert window.category_dialog is None


def test_set_categories(window, sample_categories):
    """Test setting categories"""
    window.set_categories(sample_categories)
    
    # Check that categories are set in add expense widget
    assert window.add_expense_widget.categories == sample_categories
    
    # Category dialog should not be created yet
    assert window.category_dialog is None


def test_set_expenses(window, sample_expenses, sample_categories):
    """Test setting expenses"""
    window.set_expenses(sample_expenses, sample_categories)
    
    # Check that expenses are set in expense list widget
    assert window.expense_list.expenses == sample_expenses
    assert window.expense_list.categories == sample_categories


def test_set_budget(window):
    """Test setting budget"""
    window.set_budget(1000, 7000, 30000)
    
    # Check that budget is set in budget widget
    assert window.budget_widget.daily_budget == 1000
    assert window.budget_widget.weekly_budget == 7000
    assert window.budget_widget.monthly_budget == 30000


def test_set_spent(window):
    """Test setting spent amounts"""
    window.set_spent(500, 3500, 15000)
    
    # Check that spent amounts are set in budget widget
    assert window.budget_widget.daily_spent == 500
    assert window.budget_widget.weekly_spent == 3500
    assert window.budget_widget.monthly_spent == 15000


def test_show_categories_dialog(window, sample_categories, monkeypatch):
    """Test showing categories dialog"""
    window.set_categories(sample_categories)
    
    # Mock CategoryDialog.exec to avoid actually showing the dialog
    exec_called = False
    
    def mock_exec(*args, **kwargs):
        nonlocal exec_called
        exec_called = True
        return 0  # Dialog result code
    
    # Patch the CategoryDialog class to return our mock
    class MockCategoryDialog(CategoryDialog):
        def exec(self):
            return mock_exec()
    
    monkeypatch.setattr("bookkeeper.view.main_window.CategoryDialog", MockCategoryDialog)
    
    # Show the dialog
    window.show_categories_dialog()
    
    # Check that dialog was created and exec was called
    assert window.category_dialog is not None
    assert exec_called is True
    
    # Check that categories were set in the dialog
    assert window.category_dialog.category_widget.categories == sample_categories


def test_refresh_data(window, monkeypatch):
    """Test refresh data button"""
    # Set up a flag to check if the refresh signal was emitted
    refresh_called = False
    
    def mock_refresh_handler():
        nonlocal refresh_called
        refresh_called = True
    
    # Connect our mock handler to the refresh_requested signal
    window.refresh_requested.connect(mock_refresh_handler)
    
    # Click the refresh button
    QTest.mouseClick(window.refresh_button, Qt.LeftButton)
    
    # Check that the refresh signal was emitted
    assert refresh_called is True
