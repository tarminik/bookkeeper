"""
Tests for the AddExpenseWidget
"""

import pytest
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt, QDateTime

from bookkeeper.view.add_expense_widget import AddExpenseWidget
from bookkeeper.models.category import Category


@pytest.fixture
def widget(qapp):
    """Create AddExpenseWidget instance for tests"""
    widget = AddExpenseWidget()
    yield widget
    widget.deleteLater()


@pytest.fixture
def sample_categories():
    """Create sample categories for tests"""
    return {
        1: Category(pk=1, name="Food", parent=None),
        2: Category(pk=2, name="Groceries", parent=None),
        3: Category(pk=3, name="Entertainment", parent=None)
    }


def test_init(widget):
    """Test widget initialization"""
    assert widget.categories == {}
    assert widget.amount_spin is not None
    assert widget.category_combo is not None
    assert widget.date_edit is not None
    assert widget.comment_edit is not None
    assert widget.add_button is not None


def test_set_categories(widget, sample_categories):
    """Test setting categories"""
    widget.set_categories(sample_categories)
    
    assert widget.categories == sample_categories
    assert widget.category_combo.count() == 3
    
    # Check that categories are sorted alphabetically
    assert widget.category_combo.itemText(0) == "Entertainment"
    assert widget.category_combo.itemData(0) == 3
    
    assert widget.category_combo.itemText(1) == "Food"
    assert widget.category_combo.itemData(1) == 1
    
    assert widget.category_combo.itemText(2) == "Groceries"
    assert widget.category_combo.itemData(2) == 2


def test_add_expense_no_categories(widget, monkeypatch):
    """Test add expense with no categories"""
    # Mock QMessageBox.warning
    warning_shown = False
    
    def mock_warning(*args, **kwargs):
        nonlocal warning_shown
        warning_shown = True
        return QMessageBox.Ok
    
    monkeypatch.setattr("PyQt5.QtWidgets.QMessageBox.warning", mock_warning)
    
    # Try to add expense with no categories
    widget.add_expense()
    
    # Check that warning was shown
    assert warning_shown is True


def test_add_expense_with_categories(widget, sample_categories):
    """Test add expense with categories"""
    widget.set_categories(sample_categories)
    
    # Set form values
    widget.amount_spin.setValue(25)  # $25
    widget.category_combo.setCurrentIndex(1)  # "Food"
    test_date = QDateTime.fromString("2025-04-02 10:00:00", "yyyy-MM-dd hh:mm:ss")
    widget.date_edit.setDateTime(test_date)
    widget.comment_edit.setText("Test expense")
    
    # Проверяем, что метод add_expense существует и может быть вызван
    # В реальном приложении этот метод будет вызываться при нажатии на кнопку
    # и обрабатываться презентером
    widget.add_expense()
    
    # Проверяем, что значения формы не изменились после вызова метода
    assert widget.amount_spin.value() == 25
    assert widget.category_combo.currentIndex() == 1
    assert widget.date_edit.dateTime() == test_date
    assert widget.comment_edit.text() == "Test expense"


def test_clear_form(widget, sample_categories):
    """Test clearing form"""
    widget.set_categories(sample_categories)
    
    # Set form values
    widget.amount_spin.setValue(25)  # $25
    widget.category_combo.setCurrentIndex(1)  # "Food"
    test_date = QDateTime.fromString("2025-04-02 10:00:00", "yyyy-MM-dd hh:mm:ss")
    widget.date_edit.setDateTime(test_date)
    widget.comment_edit.setText("Test expense")
    
    # Clear form
    widget.clear_form()
    
    # Check that form is cleared
    assert widget.amount_spin.value() == 0
    assert widget.comment_edit.text() == ""
    
    # Date should be reset to current date/time, which is hard to test exactly
    # So we just check that it's different from our test date
    assert widget.date_edit.dateTime() != test_date
    
    # Category should be the first one
    assert widget.category_combo.currentIndex() == 0
