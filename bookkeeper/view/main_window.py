"""
Main window for the Bookkeeper application
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QDialog, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal

from bookkeeper.view.expense_list_widget import ExpenseListWidget
from bookkeeper.view.budget_widget import BudgetWidget
from bookkeeper.view.add_expense_widget import AddExpenseWidget
from bookkeeper.view.category_widget import CategoryWidget


class CategoryDialog(QDialog):
    """Dialog for managing categories"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Categories")
        self.setMinimumSize(400, 500)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create category widget
        self.category_widget = CategoryWidget(self)
        layout.addWidget(self.category_widget)
        
        # Create close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        self.setLayout(layout)
    
    def set_categories(self, categories):
        """
        Set the categories to display
        
        Parameters
        ----------
        categories : dict[int, Category]
            Dictionary mapping category IDs to Category objects
        """
        self.category_widget.set_categories(categories)


class MainWindow(QMainWindow):
    """Main window for the Bookkeeper application"""
    # Signal emitted when refresh button is clicked
    refresh_requested = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bookkeeper - Personal Finance Manager")
        self.setMinimumSize(800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Create expense tab
        expense_tab = QWidget()
        expense_layout = QVBoxLayout(expense_tab)
        
        # Add expense list widget
        self.expense_list = ExpenseListWidget()
        expense_layout.addWidget(self.expense_list)
        
        self.tabs.addTab(expense_tab, "Expenses")
        
        # Create budget tab
        budget_tab = QWidget()
        budget_layout = QVBoxLayout(budget_tab)
        
        # Add budget widget
        self.budget_widget = BudgetWidget()
        budget_layout.addWidget(self.budget_widget)
        
        self.tabs.addTab(budget_tab, "Budget")
        
        # Create add expense tab
        add_expense_tab = QWidget()
        add_expense_layout = QVBoxLayout(add_expense_tab)
        
        # Add expense widget
        self.add_expense_widget = AddExpenseWidget()
        add_expense_layout.addWidget(self.add_expense_widget)
        
        self.tabs.addTab(add_expense_tab, "Add Expense")
        
        # Create bottom buttons layout
        buttons_layout = QHBoxLayout()
        
        # Add manage categories button
        self.categories_button = QPushButton("Manage Categories")
        self.categories_button.clicked.connect(self.show_categories_dialog)
        buttons_layout.addWidget(self.categories_button)
        
        # Add refresh button
        self.refresh_button = QPushButton("Refresh Data")
        self.refresh_button.clicked.connect(self.refresh_data)
        buttons_layout.addWidget(self.refresh_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Create category dialog
        self.category_dialog = None
        
        # The presenter will handle data initialization
    
    def show_categories_dialog(self):
        """Show the categories dialog"""
        if not self.category_dialog:
            self.category_dialog = CategoryDialog(self)
        
        # Pass the current categories to the dialog
        if hasattr(self, 'categories'):
            self.category_dialog.set_categories(self.categories)
        else:
            self.category_dialog.set_categories({})
        
        self.category_dialog.exec()
    
    def refresh_data(self):
        """Refresh all data from the repository"""
        # Emit the refresh_requested signal
        self.refresh_requested.emit()
        
    def set_categories(self, categories):
        """
        Set the categories for all widgets
        
        Parameters
        ----------
        categories : dict[int, Category]
            Dictionary mapping category IDs to Category objects
        """
        # Store the categories for later use
        self.categories = categories
        
        self.add_expense_widget.set_categories(categories)
        # Also update the category dialog if it exists
        if self.category_dialog:
            self.category_dialog.set_categories(categories)
    
    def set_expenses(self, expenses, categories=None):
        """
        Set the expenses for the expense list widget
        
        Parameters
        ----------
        expenses : list[Expense]
            List of expenses to display
        categories : dict[int, Category], optional
            Dictionary mapping category IDs to Category objects
        """
        self.expense_list.set_expenses(expenses, categories)
    
    def set_budget(self, daily=0, weekly=0, monthly=0):
        """
        Set the budget values
        
        Parameters
        ----------
        daily : int
            Daily budget in cents
        weekly : int
            Weekly budget in cents
        monthly : int
            Monthly budget in cents
        """
        self.budget_widget.set_budgets(daily, weekly, monthly)
    
    def set_spent(self, daily_spent=0, weekly_spent=0, monthly_spent=0):
        """
        Set the spent amounts
        
        Parameters
        ----------
        daily_spent : int
            Amount spent today in cents
        weekly_spent : int
            Amount spent this week in cents
        monthly_spent : int
            Amount spent this month in cents
        """
        self.budget_widget.set_spent(daily_spent, weekly_spent, monthly_spent)
