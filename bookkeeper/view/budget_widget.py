"""
Widget for displaying and editing budget information
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, 
    QComboBox, QGroupBox, QFormLayout, QPushButton
)
from PyQt5.QtCore import Qt


class BudgetWidget(QWidget):
    """
    Widget for displaying and editing budget information
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.daily_budget = 0
        self.weekly_budget = 0
        self.monthly_budget = 0
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components"""
        # Main layout
        main_layout = QVBoxLayout(self)

        # Budget settings group
        budget_group = QGroupBox("Budget Settings")
        budget_layout = QFormLayout()

        # Daily budget
        self.daily_budget_spin = QSpinBox()
        self.daily_budget_spin.setRange(0, 1000000)
        self.daily_budget_spin.setSingleStep(100)
        self.daily_budget_spin.setPrefix("$")
        self.daily_budget_spin.valueChanged.connect(self.on_daily_budget_changed)
        budget_layout.addRow("Daily Budget:", self.daily_budget_spin)

        # Weekly budget
        self.weekly_budget_spin = QSpinBox()
        self.weekly_budget_spin.setRange(0, 10000000)
        self.weekly_budget_spin.setSingleStep(500)
        self.weekly_budget_spin.setPrefix("$")
        self.weekly_budget_spin.valueChanged.connect(self.on_weekly_budget_changed)
        budget_layout.addRow("Weekly Budget:", self.weekly_budget_spin)

        # Monthly budget
        self.monthly_budget_spin = QSpinBox()
        self.monthly_budget_spin.setRange(0, 100000000)
        self.monthly_budget_spin.setSingleStep(1000)
        self.monthly_budget_spin.setPrefix("$")
        self.monthly_budget_spin.valueChanged.connect(self.on_monthly_budget_changed)
        budget_layout.addRow("Monthly Budget:", self.monthly_budget_spin)

        budget_group.setLayout(budget_layout)
        main_layout.addWidget(budget_group)

        # Budget status group
        status_group = QGroupBox("Budget Status")
        status_layout = QVBoxLayout()

        # Period selection
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel("View period:"))
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Daily", "Weekly", "Monthly"])
        self.period_combo.currentIndexChanged.connect(self.update_status)
        period_layout.addWidget(self.period_combo)
        status_layout.addLayout(period_layout)

        # Status information
        self.status_layout = QFormLayout()
        self.budget_label = QLabel("$0.00")
        self.spent_label = QLabel("$0.00")
        self.remaining_label = QLabel("$0.00")
        
        self.status_layout.addRow("Budget:", self.budget_label)
        self.status_layout.addRow("Spent:", self.spent_label)
        self.status_layout.addRow("Remaining:", self.remaining_label)
        
        status_layout.addLayout(self.status_layout)
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)

        # Save button
        self.save_button = QPushButton("Save Budget Settings")
        self.save_button.clicked.connect(self.save_budget)
        main_layout.addWidget(self.save_button)

        # Set the main layout
        self.setLayout(main_layout)
        
        # Initialize with default values
        self.update_status()

    def set_budgets(self, daily=0, weekly=0, monthly=0):
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
        self.daily_budget = daily
        self.weekly_budget = weekly
        self.monthly_budget = monthly
        
        # Update the UI (convert from cents to dollars)
        self.daily_budget_spin.setValue(daily // 100)
        self.weekly_budget_spin.setValue(weekly // 100)
        self.monthly_budget_spin.setValue(monthly // 100)
        
        self.update_status()

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
        self.daily_spent = daily_spent
        self.weekly_spent = weekly_spent
        self.monthly_spent = monthly_spent
        self.update_status()

    def update_status(self):
        """Update the status display based on the selected period"""
        period = self.period_combo.currentText()
        
        if period == "Daily":
            budget = self.daily_budget
            spent = getattr(self, 'daily_spent', 0)
        elif period == "Weekly":
            budget = self.weekly_budget
            spent = getattr(self, 'weekly_spent', 0)
        else:  # Monthly
            budget = self.monthly_budget
            spent = getattr(self, 'monthly_spent', 0)
        
        remaining = max(0, budget - spent)
        
        # Update labels (convert from cents to dollars)
        self.budget_label.setText(f"${budget / 100:.2f}")
        self.spent_label.setText(f"${spent / 100:.2f}")
        self.remaining_label.setText(f"${remaining / 100:.2f}")

    def on_daily_budget_changed(self, value):
        """
        Handle daily budget changes
        
        Parameters
        ----------
        value : int
            New value in dollars
        """
        self.daily_budget = value * 100  # Convert to cents
        self.update_status()

    def on_weekly_budget_changed(self, value):
        """
        Handle weekly budget changes
        
        Parameters
        ----------
        value : int
            New value in dollars
        """
        self.weekly_budget = value * 100  # Convert to cents
        self.update_status()

    def on_monthly_budget_changed(self, value):
        """
        Handle monthly budget changes
        
        Parameters
        ----------
        value : int
            New value in dollars
        """
        self.monthly_budget = value * 100  # Convert to cents
        self.update_status()

    def save_budget(self):
        """Save the budget settings"""
        # This will be handled by the presenter
        # The presenter will get the values from the properties
        pass
