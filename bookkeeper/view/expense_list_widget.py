"""
Widget for displaying and editing the list of expenses
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QHBoxLayout, QHeaderView, QMessageBox
)
from PyQt5.QtCore import Qt

from bookkeeper.models.expense import Expense
from bookkeeper.models.category import Category


class ExpenseListWidget(QWidget):
    """
    Widget for displaying and editing the list of expenses
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.expenses = []
        self.categories = {}
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components"""
        # Main layout
        main_layout = QVBoxLayout(self)

        # Create table for expenses
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Date", "Category", "Amount", "Comment"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        main_layout.addWidget(self.table)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Edit button
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_expense)
        buttons_layout.addWidget(self.edit_button)
        
        # Delete button
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_expense)
        buttons_layout.addWidget(self.delete_button)
        
        main_layout.addLayout(buttons_layout)
        
        self.setLayout(main_layout)

    def set_expenses(self, expenses, categories_dict=None):
        """
        Set the expenses to display
        
        Parameters
        ----------
        expenses : list[Expense]
            List of expenses to display
        categories_dict : dict[int, Category], optional
            Dictionary mapping category IDs to Category objects
        """
        self.expenses = expenses
        if categories_dict:
            self.categories = categories_dict
        self.update_table()

    def update_table(self):
        """Update the table with current expenses"""
        self.table.setRowCount(0)  # Clear the table
        
        for expense in self.expenses:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            
            # ID
            self.table.setItem(row_position, 0, QTableWidgetItem(str(expense.pk)))
            
            # Date
            date_str = expense.expense_date.strftime("%Y-%m-%d %H:%M")
            self.table.setItem(row_position, 1, QTableWidgetItem(date_str))
            
            # Category
            category_name = "Unknown"
            if expense.category in self.categories:
                category_name = self.categories[expense.category].name
            self.table.setItem(row_position, 2, QTableWidgetItem(category_name))
            
            # Amount
            amount_str = f"{expense.amount / 100:.2f}"  # Convert cents to dollars/euros
            self.table.setItem(row_position, 3, QTableWidgetItem(amount_str))
            
            # Comment
            self.table.setItem(row_position, 4, QTableWidgetItem(expense.comment))

    def edit_expense(self):
        """Edit the selected expense"""
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "No expense selected")
            return
        
        # Get the expense ID from the first column of the selected row
        row = selected_rows[0].row()
        expense_id = int(self.table.item(row, 0).text())
        
        # Find the expense in the list
        expense = next((e for e in self.expenses if e.pk == expense_id), None)
        if expense:
            # This will be handled by the presenter
            pass
            
    def get_selected_expense_id(self):
        """Get the ID of the selected expense
        
        Returns
        -------
        int or None
            ID of the selected expense, or None if no expense is selected
        """
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            return None
            
        row = selected_rows[0].row()
        try:
            expense_id = int(self.table.item(row, 0).text())
            return expense_id
        except (ValueError, AttributeError):
            return None

    def delete_expense(self):
        """Delete the selected expense"""
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "No expense selected")
            return
        
        # Get the expense ID from the first column of the selected row
        row = selected_rows[0].row()
        expense_id = int(self.table.item(row, 0).text())
        
        # Confirm deletion
        reply = QMessageBox.question(self, "Confirm Deletion", 
                                    f"Are you sure you want to delete expense {expense_id}?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # This will be handled by the presenter
            pass
            
    def get_delete_confirmation(self, expense_id):
        """Get confirmation for deleting an expense
        
        Parameters
        ----------
        expense_id : int
            ID of the expense to delete
            
        Returns
        -------
        bool
            True if deletion is confirmed, False otherwise
        """
        reply = QMessageBox.question(self, "Confirm Deletion", 
                                  f"Are you sure you want to delete expense {expense_id}?",
                                  QMessageBox.Yes | QMessageBox.No)
        return reply == QMessageBox.Yes
