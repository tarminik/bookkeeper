"""
Widget for adding new expenses
"""

from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDateTimeEdit, QSpinBox, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt, QDateTime


class AddExpenseWidget(QWidget):
    """
    Widget for adding new expenses
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.categories = {}  # Dictionary of category_id: Category
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components"""
        # Main layout
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Amount field
        self.amount_spin = QSpinBox()
        self.amount_spin.setRange(0, 1000000)  # Up to 10,000 in dollars/euros
        self.amount_spin.setSingleStep(100)
        self.amount_spin.setPrefix("$")
        self.amount_spin.setSuffix(".00")
        form_layout.addRow("Amount:", self.amount_spin)

        # Category dropdown
        self.category_combo = QComboBox()
        form_layout.addRow("Category:", self.category_combo)

        # Date field
        self.date_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow("Date:", self.date_edit)

        # Comment field
        self.comment_edit = QLineEdit()
        form_layout.addRow("Comment:", self.comment_edit)

        main_layout.addLayout(form_layout)

        # Add button
        self.add_button = QPushButton("Add Expense")
        self.add_button.clicked.connect(self.add_expense)
        main_layout.addWidget(self.add_button)

        # Set the main layout
        self.setLayout(main_layout)

    def set_categories(self, categories):
        """
        Set the available categories for selection
        
        Parameters
        ----------
        categories : dict[int, Category]
            Dictionary mapping category IDs to Category objects
        """
        self.categories = categories
        self.update_category_combo()

    def update_category_combo(self):
        """Update the category dropdown with current categories"""
        self.category_combo.clear()
        
        # Add categories sorted by name
        sorted_categories = sorted(self.categories.values(), key=lambda c: c.name)
        for category in sorted_categories:
            self.category_combo.addItem(category.name, category.pk)

    def add_expense(self):
        """Add a new expense"""
        # Validate inputs
        if self.category_combo.count() == 0:
            QMessageBox.warning(self, "Warning", "No categories available. Please add a category first.")
            return
        
        # The actual adding will be handled by the presenter
        # The presenter will get the values from the form fields
        pass

    def clear_form(self):
        """Clear all form fields"""
        self.amount_spin.setValue(0)
        self.date_edit.setDateTime(QDateTime.currentDateTime())
        self.comment_edit.clear()
        if self.category_combo.count() > 0:
            self.category_combo.setCurrentIndex(0)
