"""
Presenter component for the Bookkeeper application.

This module implements the Presenter component of the MVP (Model-View-Presenter) pattern.
The Presenter acts as an intermediary between the Model (repository) and the View (GUI).
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Type, TypeVar, Any

from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.models.budget import Budget
from bookkeeper.repository.abstract_repository import AbstractRepository
from bookkeeper.repository.sqlite_repository import SqliteRepository
from bookkeeper.view.main_window import MainWindow

T = TypeVar('T')


class BookkeeperPresenter:
    """
    Presenter for the Bookkeeper application.
    
    Connects the model (repositories) with the view (GUI).
    """
    
    def __init__(self, db_path: str, main_window: MainWindow) -> None:
        """
        Initialize the presenter.
        
        Parameters
        ----------
        db_path : str
            Path to the SQLite database file
        main_window : MainWindow
            The main window of the application
        """
        self.db_path = db_path
        self.main_window = main_window
        
        # Initialize repositories
        self.category_repo = SqliteRepository(db_path, Category)
        self.expense_repo = SqliteRepository(db_path, Expense)
        self.budget_repo = SqliteRepository(db_path, Budget)
        
        # Connect signals to slots
        self._connect_signals()
        
        # Load initial data
        self.load_data()
    
    def _connect_signals(self) -> None:
        """Connect GUI signals to presenter methods"""
        # Connect refresh button
        self.main_window.refresh_button.clicked.connect(self.load_data)
        
        # Connect add expense button
        self.main_window.add_expense_widget.add_button.clicked.connect(self.add_expense)
        
        # Connect budget save button
        self.main_window.budget_widget.save_button.clicked.connect(self.save_budget)
        
        # Connect category dialog signals
        if self.main_window.category_dialog:
            cat_widget = self.main_window.category_dialog.category_widget
            cat_widget.add_button.clicked.connect(self.add_category)
            cat_widget.add_sub_button.clicked.connect(self.add_subcategory)
            cat_widget.edit_button.clicked.connect(self.edit_category)
            cat_widget.delete_button.clicked.connect(self.delete_category)
    
    def load_data(self) -> None:
        """Load all data from repositories and update the UI"""
        self.load_categories()
        self.load_expenses()
        self.load_budget()
    
    def load_categories(self) -> None:
        """Load categories from repository and update the UI"""
        categories = self.category_repo.get_all()
        
        # Convert list to dictionary for easier access
        categories_dict = {cat.pk: cat for cat in categories}
        
        # Update UI
        self.main_window.set_categories(categories_dict)
    
    def load_expenses(self) -> None:
        """Load expenses from repository and update the UI"""
        expenses = self.expense_repo.get_all()
        
        # Get categories for display
        categories = self.category_repo.get_all()
        categories_dict = {cat.pk: cat for cat in categories}
        
        # Update UI
        self.main_window.set_expenses(expenses, categories_dict)
        
        # Update spent amounts
        self._update_spent_amounts(expenses)
    
    def load_budget(self) -> None:
        """Load budget from repository and update the UI"""
        budgets = self.budget_repo.get_all()
        
        daily_budget = 0
        weekly_budget = 0
        monthly_budget = 0
        
        # Find the most recent budget
        if budgets:
            latest_budget = max(budgets, key=lambda b: b.date)
            daily_budget = latest_budget.daily_amount
            weekly_budget = latest_budget.weekly_amount
            monthly_budget = latest_budget.monthly_amount
        
        # Update UI
        self.main_window.set_budget(daily_budget, weekly_budget, monthly_budget)
    
    def _update_spent_amounts(self, expenses: List[Expense]) -> None:
        """
        Calculate and update spent amounts
        
        Parameters
        ----------
        expenses : List[Expense]
            List of all expenses
        """
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        
        daily_spent = sum(e.amount for e in expenses if e.expense_date >= today)
        weekly_spent = sum(e.amount for e in expenses if e.expense_date >= week_start)
        monthly_spent = sum(e.amount for e in expenses if e.expense_date >= month_start)
        
        # Update UI
        self.main_window.set_spent(daily_spent, weekly_spent, monthly_spent)
    
    def add_expense(self) -> None:
        """Add a new expense"""
        # Get values from the UI
        amount = self.main_window.add_expense_widget.amount_spin.value() * 100  # Convert to cents
        category_id = self.main_window.add_expense_widget.category_combo.currentData()
        expense_date = self.main_window.add_expense_widget.date_edit.dateTime().toPython()
        comment = self.main_window.add_expense_widget.comment_edit.text()
        
        # Create and save the expense
        expense = Expense(
            pk=0,  # Will be set by repository
            amount=amount,
            category=category_id,
            expense_date=expense_date,
            comment=comment
        )
        
        self.expense_repo.add(expense)
        
        # Clear the form and reload data
        self.main_window.add_expense_widget.clear_form()
        self.load_expenses()
    
    def save_budget(self) -> None:
        """Save budget settings"""
        # Get values from the UI
        daily_budget = self.main_window.budget_widget.daily_budget
        weekly_budget = self.main_window.budget_widget.weekly_budget
        monthly_budget = self.main_window.budget_widget.monthly_budget
        
        # Create and save the budget
        budget = Budget(
            pk=0,  # Will be set by repository
            date=datetime.now(),
            daily_amount=daily_budget,
            weekly_amount=weekly_budget,
            monthly_amount=monthly_budget
        )
        
        self.budget_repo.add(budget)
        
        # Reload data
        self.load_budget()
    
    def add_category(self) -> None:
        """Add a new root category"""
        if not self.main_window.category_dialog:
            return
            
        # Get name from dialog
        name, ok = self.main_window.category_dialog.category_widget.get_category_name()
        if not ok or not name:
            return
        
        # Create and save the category
        category = Category(
            pk=0,  # Will be set by repository
            name=name,
            parent=None
        )
        
        self.category_repo.add(category)
        
        # Reload data
        self.load_categories()
    
    def add_subcategory(self) -> None:
        """Add a subcategory to the selected category"""
        if not self.main_window.category_dialog:
            return
            
        # Get parent category and name from dialog
        parent_id, name, ok = self.main_window.category_dialog.category_widget.get_subcategory_info()
        if not ok or not name or parent_id is None:
            return
        
        # Create and save the subcategory
        category = Category(
            pk=0,  # Will be set by repository
            name=name,
            parent=parent_id
        )
        
        self.category_repo.add(category)
        
        # Reload data
        self.load_categories()
    
    def edit_category(self) -> None:
        """Edit the selected category"""
        if not self.main_window.category_dialog:
            return
            
        # Get category ID and new name from dialog
        category_id, name, ok = self.main_window.category_dialog.category_widget.get_edit_info()
        if not ok or not name or category_id is None:
            return
        
        # Get the category from repository
        category = self.category_repo.get(category_id)
        if not category:
            return
        
        # Update and save the category
        category.name = name
        self.category_repo.update(category)
        
        # Reload data
        self.load_categories()
    
    def delete_category(self) -> None:
        """Delete the selected category"""
        if not self.main_window.category_dialog:
            return
            
        # Get category ID from dialog
        category_id, ok = self.main_window.category_dialog.category_widget.get_delete_info()
        if not ok or category_id is None:
            return
        
        # Delete the category
        try:
            self.category_repo.delete(category_id)
            
            # Also delete all subcategories
            subcategories = self.category_repo.get_all({"parent": category_id})
            for subcat in subcategories:
                self.category_repo.delete(subcat.pk)
                
            # Reload data
            self.load_categories()
        except KeyError:
            # Category not found, already deleted
            pass
