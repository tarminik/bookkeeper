"""
Tests for the BudgetWidget
"""

import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

from bookkeeper.view.budget_widget import BudgetWidget


@pytest.fixture
def widget(qapp):
    """Create BudgetWidget instance for tests"""
    widget = BudgetWidget()
    yield widget
    widget.deleteLater()


def test_init(widget):
    """Test widget initialization"""
    # Check initial budget values
    assert widget.daily_budget == 0
    assert widget.weekly_budget == 0
    assert widget.monthly_budget == 0
    
    # Check UI components
    assert widget.daily_budget_spin is not None
    assert widget.weekly_budget_spin is not None
    assert widget.monthly_budget_spin is not None
    assert widget.budget_label is not None
    assert widget.spent_label is not None
    assert widget.remaining_label is not None
    assert widget.save_button is not None


def test_set_budgets(widget):
    """Test setting budget values"""
    # Set budget values
    widget.set_budgets(1000, 7000, 30000)
    
    # Check budget values
    assert widget.daily_budget == 1000
    assert widget.weekly_budget == 7000
    assert widget.monthly_budget == 30000
    
    # Check UI components
    assert widget.daily_budget_spin.value() == 10  # 1000 cents = $10
    assert widget.weekly_budget_spin.value() == 70  # 7000 cents = $70
    assert widget.monthly_budget_spin.value() == 300  # 30000 cents = $300
    
    # Check that status is updated
    assert widget.budget_label.text() == "$10.00"  # Default view is daily


def test_set_spent(widget):
    """Test setting spent amounts"""
    # Set budget values
    widget.set_budgets(1000, 7000, 30000)
    
    # Set spent values
    widget.set_spent(500, 3500, 15000)
    
    # Check spent values
    assert widget.daily_spent == 500
    assert widget.weekly_spent == 3500
    assert widget.monthly_spent == 15000
    
    # Check that status is updated for daily view
    assert widget.budget_label.text() == "$10.00"
    assert widget.spent_label.text() == "$5.00"
    assert widget.remaining_label.text() == "$5.00"
    
    # Switch to weekly view
    widget.period_combo.setCurrentIndex(1)
    assert widget.budget_label.text() == "$70.00"
    assert widget.spent_label.text() == "$35.00"
    assert widget.remaining_label.text() == "$35.00"
    
    # Switch to monthly view
    widget.period_combo.setCurrentIndex(2)
    assert widget.budget_label.text() == "$300.00"
    assert widget.spent_label.text() == "$150.00"
    assert widget.remaining_label.text() == "$150.00"


def test_budget_changes(widget):
    """Test budget value changes"""
    # Change daily budget
    widget.daily_budget_spin.setValue(20)  # $20 = 2000 cents
    assert widget.daily_budget == 2000
    
    # Change weekly budget
    widget.weekly_budget_spin.setValue(100)  # $100 = 10000 cents
    assert widget.weekly_budget == 10000
    
    # Change monthly budget
    widget.monthly_budget_spin.setValue(500)  # $500 = 50000 cents
    assert widget.monthly_budget == 50000


def test_save_budget(widget):
    """Test save budget method"""
    # Установка тестовых значений бюджета
    widget.set_budgets(1000, 7000, 30000)
    
    # Проверка, что метод save_budget существует и может быть вызван
    # В реальном приложении этот метод будет вызываться при нажатии на кнопку
    # и обрабатываться презентером
    widget.save_budget()
    
    # Проверка, что значения бюджета не изменились после вызова метода
    assert widget.daily_budget == 1000
    assert widget.weekly_budget == 7000
    assert widget.monthly_budget == 30000
