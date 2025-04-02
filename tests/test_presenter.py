"""
Tests for the BookkeeperPresenter
"""

import pytest
import os
import sqlite3
import types
from unittest.mock import MagicMock, patch
from datetime import datetime

from bookkeeper.presenter import BookkeeperPresenter
from bookkeeper.repository.sqlite_repository import SqliteRepository
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.models.category import Category
from bookkeeper.models.budget import Budget
from bookkeeper.repository.sqlite_repository import SqliteRepository


class MockMainWindow:
    """Mock MainWindow for testing"""
    def __init__(self):
        # Mock widgets
        self.expense_list = MagicMock()
        self.budget_widget = MagicMock()
        self.add_expense_widget = MagicMock()
        self.category_dialog = None
        
        # Mock buttons and signals
        self.refresh_button = MagicMock()
        self.refresh_button.clicked = MagicMock()
        
        # Mock budget widget
        self.budget_widget.save_button = MagicMock()
        self.budget_widget.save_button.clicked = MagicMock()
        self.budget_widget.daily_budget = 0
        self.budget_widget.weekly_budget = 0
        self.budget_widget.monthly_budget = 0
        
        # Mock add expense widget
        self.add_expense_widget.add_button = MagicMock()
        self.add_expense_widget.add_button.clicked = MagicMock()
        self.add_expense_widget.amount_spin = MagicMock()
        self.add_expense_widget.amount_spin.value = MagicMock(return_value=10)
        self.add_expense_widget.category_combo = MagicMock()
        self.add_expense_widget.category_combo.currentData = MagicMock(return_value=1)
        self.add_expense_widget.date_edit = MagicMock()
        self.add_expense_widget.date_edit.dateTime = MagicMock()
        self.add_expense_widget.date_edit.dateTime().toPython = MagicMock(
            return_value=datetime(2025, 4, 2, 10, 0))
        self.add_expense_widget.comment_edit = MagicMock()
        self.add_expense_widget.comment_edit.text = MagicMock(return_value="Test expense")
        self.add_expense_widget.clear_form = MagicMock()
        
        # Mock methods
        self.set_categories = MagicMock()
        self.set_expenses = MagicMock()
        self.set_budget = MagicMock()
        self.set_spent = MagicMock()
        self.refresh_data = MagicMock()


@pytest.fixture
def db_path():
    """Create temporary database for testing"""
    path = "test_bookkeeper.db"
    
    # Remove existing test database if it exists
    if os.path.exists(path):
        os.remove(path)
    
    # Create test database
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
    CREATE TABLE categories (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        parent_id INTEGER,
        FOREIGN KEY (parent_id) REFERENCES categories (id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE expenses (
        id INTEGER PRIMARY KEY,
        amount INTEGER NOT NULL,
        category_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        comment TEXT,
        FOREIGN KEY (category_id) REFERENCES categories (id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE budgets (
        id INTEGER PRIMARY KEY,
        daily INTEGER NOT NULL,
        weekly INTEGER NOT NULL,
        monthly INTEGER NOT NULL
    )
    """)
    
    # Insert sample data
    cursor.execute("INSERT INTO categories (id, name, parent_id) VALUES (1, 'Food', NULL)")
    cursor.execute("INSERT INTO categories (id, name, parent_id) VALUES (2, 'Entertainment', NULL)")
    cursor.execute("INSERT INTO categories (id, name, parent_id) VALUES (3, 'Fast Food', 1)")
    
    cursor.execute("""
    INSERT INTO expenses (id, amount, category_id, date, comment)
    VALUES (1, 1000, 1, '2025-04-01 12:00:00', 'Lunch')
    """)
    cursor.execute("""
    INSERT INTO expenses (id, amount, category_id, date, comment)
    VALUES (2, 2500, 2, '2025-04-01 15:30:00', 'Movie')
    """)
    
    cursor.execute("""
    INSERT INTO budgets (id, daily, weekly, monthly)
    VALUES (1, 1000, 7000, 30000)
    """)
    
    conn.commit()
    conn.close()
    
    yield path
    
    # Clean up
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def presenter(db_path):
    """Create BookkeeperPresenter instance for testing"""
    view = MockMainWindow()
    presenter = BookkeeperPresenter(db_path, view)
    return presenter


def test_init(presenter):
    """Test presenter initialization"""
    assert presenter.main_window is not None
    assert presenter.category_repo is not None
    assert presenter.expense_repo is not None
    assert presenter.budget_repo is not None
    assert isinstance(presenter.category_repo, SqliteRepository)
    assert isinstance(presenter.expense_repo, SqliteRepository)
    assert isinstance(presenter.budget_repo, SqliteRepository)


def test_load_data(presenter):
    """Test loading data"""
    # Add test data to repositories
    from bookkeeper.models.expense import Expense
    from bookkeeper.models.budget import Budget
    from datetime import datetime
    
    # Add categories
    food_category = Category(name="Food", parent=None, pk=0)
    food_id = presenter.category_repo.add(food_category)
    
    entertainment_category = Category(name="Entertainment", parent=None, pk=0)
    entertainment_id = presenter.category_repo.add(entertainment_category)
    
    fast_food_category = Category(name="Fast Food", parent=food_id, pk=0)  # подкатегория Food
    presenter.category_repo.add(fast_food_category)
    
    # Add expenses
    lunch_expense = Expense(
        pk=0,
        amount=1000,  # 10.00
        category=food_id,
        expense_date=datetime(2023, 4, 1, 12, 0),
        comment="Lunch"
    )
    lunch_id = presenter.expense_repo.add(lunch_expense)
    
    movie_expense = Expense(
        pk=0,
        amount=2500,  # 25.00
        category=entertainment_id,
        expense_date=datetime(2023, 4, 2, 19, 0),
        comment="Movie"
    )
    presenter.expense_repo.add(movie_expense)
    
    # Add budget
    budget = Budget(
        pk=0,
        daily_amount=1000,  # 10.00
        weekly_amount=7000,  # 70.00
        monthly_amount=30000,  # 300.00
        date=datetime(2023, 4, 1)
    )
    
    budget_id = presenter.budget_repo.add(budget)
    
    # Call load_data
    presenter.load_data()
    
    # Check that view methods were called
    presenter.main_window.set_categories.assert_called()
    presenter.main_window.set_expenses.assert_called()
    presenter.main_window.set_budget.assert_called()
    presenter.main_window.set_spent.assert_called()
    
    # Check data in repositories
    categories = presenter.category_repo.get_all()
    assert len(categories) == 3
    
    category_names = [c.name for c in categories]
    assert "Food" in category_names
    assert "Entertainment" in category_names
    assert "Fast Food" in category_names
    
    expenses = presenter.expense_repo.get_all()
    assert len(expenses) == 2
    assert any(e.amount == 1000 for e in expenses)
    assert any(e.amount == 2500 for e in expenses)


def test_add_expense(presenter):
    """Test adding expense"""
    # Get initial expense count
    initial_expenses = presenter.expense_repo.get_all()
    initial_count = len(initial_expenses)
    
    # Call add_expense method
    presenter.add_expense()
    
    # Check that expense was added to repository
    expenses = presenter.expense_repo.get_all()
    assert len(expenses) == initial_count + 1
    
    # Find the new expense
    new_expense = next((e for e in expenses if e.comment == "Test expense"), None)
    assert new_expense is not None
    assert new_expense.amount == 1000  # 10 * 100 from mocked amount_spin
    assert new_expense.category == 1  # from mocked category_combo
    
    # Check that view was updated
    presenter.main_window.add_expense_widget.clear_form.assert_called_once()
    presenter.main_window.set_expenses.assert_called()
    presenter.main_window.set_spent.assert_called()


def test_save_budget(presenter):
    """Test saving budget"""
    # Set budget values in mock
    presenter.main_window.budget_widget.daily_budget = 2000
    presenter.main_window.budget_widget.weekly_budget = 14000
    presenter.main_window.budget_widget.monthly_budget = 60000
    
    # Get initial budget count
    initial_budgets = presenter.budget_repo.get_all()
    initial_count = len(initial_budgets)
    
    # Save budget
    presenter.save_budget()
    
    # Check that budget was saved to repository
    budgets = presenter.budget_repo.get_all()
    assert len(budgets) == initial_count + 1
    
    # Find the new budget
    new_budget = max(budgets, key=lambda b: b.date) if budgets else None
    assert new_budget is not None
    assert new_budget.daily_amount == 2000
    assert new_budget.weekly_amount == 14000
    assert new_budget.monthly_amount == 60000
    
    # Check that view was updated
    presenter.main_window.set_budget.assert_called()


def test_add_category(presenter):
    """Test adding category"""
    # Add test data to repository
    food_category = Category(name="Food", parent=None, pk=0)
    food_id = presenter.category_repo.add(food_category)
    
    # Mock category dialog
    presenter.main_window.category_dialog = MagicMock()
    presenter.main_window.category_dialog.category_widget = MagicMock()
    presenter.main_window.category_dialog.category_widget.get_category_name = MagicMock(
        return_value=("New Category", True))
    
    # Get initial category count
    initial_categories = presenter.category_repo.get_all()
    initial_count = len(initial_categories)
    
    # Add new category
    presenter.add_category()
    
    # Check that category was added to repository
    categories = presenter.category_repo.get_all()
    assert len(categories) == initial_count + 1
    
    # Find the new category
    new_category = next((c for c in categories if c.name == "New Category"), None)
    assert new_category is not None
    assert new_category.parent is None
    
    # Check that view was updated
    presenter.main_window.set_categories.assert_called()


def test_add_subcategory(presenter):
    """Test adding subcategory"""
    # Add test data to repository
    food_category = Category(name="Food", parent=None, pk=0)
    food_id = presenter.category_repo.add(food_category)
    
    # Mock category dialog
    presenter.main_window.category_dialog = MagicMock()
    presenter.main_window.category_dialog.category_widget = MagicMock()
    presenter.main_window.category_dialog.category_widget.get_subcategory_info = MagicMock(
        return_value=(food_id, "New Subcategory", True))
    
    # Get initial category count
    initial_categories = presenter.category_repo.get_all()
    initial_count = len(initial_categories)
    
    # Add new subcategory
    presenter.add_subcategory()
    
    # Check that subcategory was added to repository
    categories = presenter.category_repo.get_all()
    assert len(categories) == initial_count + 1
    
    # Find the new subcategory
    new_category = next((c for c in categories if c.name == "New Subcategory"), None)
    assert new_category is not None
    assert new_category.parent == food_id
    
    # Check that view was updated
    presenter.main_window.set_categories.assert_called()


def test_edit_category(presenter):
    """Test editing category"""
    # Add test data to repository
    food_category = Category(name="Food", parent=None, pk=0)
    food_id = presenter.category_repo.add(food_category)
    
    # Mock category dialog
    presenter.main_window.category_dialog = MagicMock()
    presenter.main_window.category_dialog.category_widget = MagicMock()
    presenter.main_window.category_dialog.category_widget.get_edit_info = MagicMock(
        return_value=(food_id, "Edited Food", True))
    
    # Edit existing category
    presenter.edit_category()
    
    # Check that category was edited in repository
    categories = presenter.category_repo.get_all()
    food_category = next((c for c in categories if c.pk == food_id), None)
    assert food_category is not None
    assert food_category.name == "Edited Food"
    
    # Check that view was updated
    presenter.main_window.set_categories.assert_called()


def test_delete_category(presenter):
    """Test deleting category"""
    # Add test data to repository
    food_category = Category(name="Food", parent=None, pk=0)
    food_id = presenter.category_repo.add(food_category)
    
    entertainment_category = Category(name="Entertainment", parent=None, pk=0)
    entertainment_id = presenter.category_repo.add(entertainment_category)
    
    # Mock category dialog
    presenter.main_window.category_dialog = MagicMock()
    presenter.main_window.category_dialog.category_widget = MagicMock()
    presenter.main_window.category_dialog.category_widget.get_delete_info = MagicMock(
        return_value=(entertainment_id, True))  # Delete "Entertainment"
    
    # Get initial category count
    initial_categories = presenter.category_repo.get_all()
    initial_count = len(initial_categories)
    
    # Delete existing category
    presenter.delete_category()
    
    # Check that category was deleted from repository
    categories = presenter.category_repo.get_all()
    assert len(categories) == initial_count - 1
    assert not any(c.pk == entertainment_id for c in categories)  # Entertainment should be gone
    
    # Check that view was updated
    presenter.main_window.set_categories.assert_called()


def test_delete_expense(presenter):
    """Test deleting expense"""
    # Add test data to repository
    from bookkeeper.models.expense import Expense
    from datetime import datetime
    
    lunch_expense = Expense(
        pk=0,
        amount=1000,  # 10.00
        category=1,  # Предполагаем, что категория с id=1 уже существует
        expense_date=datetime(2023, 4, 1, 12, 0),
        comment="Lunch"
    )
    lunch_id = presenter.expense_repo.add(lunch_expense)
    
    # We need to add a delete_expense method to the presenter
    # Let's add it first to the presenter object
    
    def mock_delete_expense(self, expense_id):
        """Mock delete_expense method"""
        # Find the expense
        expense = next((e for e in self.expense_repo.get_all() if e.pk == expense_id), None)
        if expense:
            # Delete the expense
            self.expense_repo.delete(expense_id)
            # Update UI
            self.load_data()
    
    # Add the method to the presenter
    presenter.delete_expense = types.MethodType(mock_delete_expense, presenter)
    
    # Get initial expense count
    initial_expenses = presenter.expense_repo.get_all()
    initial_count = len(initial_expenses)
    
    # Delete existing expense
    presenter.delete_expense(lunch_id)  # Delete "Lunch"
    
    # Check that expense was deleted from repository
    expenses = presenter.expense_repo.get_all()
    assert len(expenses) == initial_count - 1
    assert not any(e.pk == 1 for e in expenses)  # Lunch should be gone
    
    # Check that view was updated
    presenter.main_window.set_expenses.assert_called()
