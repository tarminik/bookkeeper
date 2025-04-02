"""
Widget for viewing and editing categories
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QInputDialog, QMessageBox, QMenu, QAction
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

from bookkeeper.models.category import Category


class CategoryWidget(QWidget):
    """
    Widget for viewing and editing categories
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.categories = {}  # Dictionary of category_id: Category
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components"""
        # Main layout
        main_layout = QVBoxLayout(self)

        # Category tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Category"])
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        main_layout.addWidget(self.tree)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Add button
        self.add_button = QPushButton("Add Category")
        self.add_button.clicked.connect(self.add_category)
        buttons_layout.addWidget(self.add_button)
        
        # Add subcategory button
        self.add_sub_button = QPushButton("Add Subcategory")
        self.add_sub_button.clicked.connect(self.add_subcategory)
        buttons_layout.addWidget(self.add_sub_button)
        
        # Edit button
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_category)
        buttons_layout.addWidget(self.edit_button)
        
        # Delete button
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_category)
        buttons_layout.addWidget(self.delete_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Set the main layout
        self.setLayout(main_layout)

    def set_categories(self, categories):
        """
        Set the categories to display
        
        Parameters
        ----------
        categories : dict[int, Category]
            Dictionary mapping category IDs to Category objects
        """
        self.categories = categories
        self.update_tree()

    def update_tree(self):
        """Update the category tree with current categories"""
        self.tree.clear()
        
        # Find root categories (those without a parent)
        root_categories = {pk: cat for pk, cat in self.categories.items() 
                          if cat.parent is None or cat.parent == 0}
        
        # Add root categories to the tree in alphabetical order
        sorted_categories = sorted(root_categories.values(), key=lambda c: c.name)
        for category in sorted_categories:
            item = QTreeWidgetItem(self.tree)
            item.setText(0, category.name)
            item.setData(0, Qt.UserRole, category.pk)
            
            # Add subcategories recursively
            self._add_subcategories(item, category.pk)
        
        # Expand all items
        self.tree.expandAll()

    def _add_subcategories(self, parent_item, parent_id):
        """
        Recursively add subcategories to the tree
        
        Parameters
        ----------
        parent_item : QTreeWidgetItem
            Parent tree item
        parent_id : int
            ID of the parent category
        """
        # Find subcategories
        subcategories = {pk: cat for pk, cat in self.categories.items() 
                        if cat.parent == parent_id}
        
        # Add subcategories to the tree in alphabetical order
        sorted_subcategories = sorted(subcategories.values(), key=lambda c: c.name)
        for category in sorted_subcategories:
            item = QTreeWidgetItem(parent_item)
            item.setText(0, category.name)
            item.setData(0, Qt.UserRole, category.pk)
            
            # Add subcategories recursively
            self._add_subcategories(item, category.pk)

    def show_context_menu(self, position):
        """
        Show context menu for the tree item
        
        Parameters
        ----------
        position : QPoint
            Position where the context menu should be shown
        """
        item = self.tree.itemAt(position)
        if not item:
            return
        
        menu = QMenu(self)
        
        # Add actions
        add_action = QAction("Add Subcategory", self)
        add_action.triggered.connect(lambda: self.add_subcategory(item))
        menu.addAction(add_action)
        
        edit_action = QAction("Edit", self)
        edit_action.triggered.connect(lambda: self.edit_category(item))
        menu.addAction(edit_action)
        
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_category(item))
        menu.addAction(delete_action)
        
        # Show the menu
        menu.exec(QCursor.pos())

    def add_category(self):
        """Add a new root category"""
        name, ok = QInputDialog.getText(self, "Add Category", "Category name:")
        if ok and name:
            # The presenter will handle this
            pass
            
    def get_category_name(self):
        """Get name for a new category
        
        Returns
        -------
        tuple[str, bool]
            Name and ok flag
        """
        return QInputDialog.getText(self, "Add Category", "Category name:")

    def add_subcategory(self, parent_item=None):
        """
        Add a subcategory to the selected category
        
        Parameters
        ----------
        parent_item : QTreeWidgetItem, optional
            Parent tree item. If None, use the currently selected item.
        """
        if parent_item is None:
            items = self.tree.selectedItems()
            if not items:
                QMessageBox.warning(self, "Warning", "No category selected")
                return
            parent_item = items[0]
        
        parent_id = parent_item.data(0, Qt.UserRole)
        parent_name = parent_item.text(0)
        
        name, ok = QInputDialog.getText(self, "Add Subcategory", 
                                       f"Subcategory name for '{parent_name}':")
        if ok and name:
            # The presenter will handle this
            pass
            
    def get_subcategory_info(self):
        """Get parent ID and name for a new subcategory
        
        Returns
        -------
        tuple[int | None, str, bool]
            Parent ID, name, and ok flag
        """
        items = self.tree.selectedItems()
        if not items:
            QMessageBox.warning(self, "Warning", "No category selected")
            return None, "", False
            
        parent_item = items[0]
        parent_id = parent_item.data(0, Qt.UserRole)
        parent_name = parent_item.text(0)
        
        name, ok = QInputDialog.getText(self, "Add Subcategory", 
                                     f"Subcategory name for '{parent_name}':")
        return parent_id, name, ok

    def edit_category(self, item=None):
        """
        Edit the selected category
        
        Parameters
        ----------
        item : QTreeWidgetItem, optional
            Tree item to edit. If None, use the currently selected item.
        """
        if item is None:
            items = self.tree.selectedItems()
            if not items:
                QMessageBox.warning(self, "Warning", "No category selected")
                return
            item = items[0]
        
        category_id = item.data(0, Qt.UserRole)
        old_name = item.text(0)
        
        name, ok = QInputDialog.getText(self, "Edit Category", 
                                       "Category name:", text=old_name)
        if ok and name:
            # The presenter will handle this
            pass
            
    def get_edit_info(self):
        """Get category ID and new name for editing
        
        Returns
        -------
        tuple[int | None, str, bool]
            Category ID, new name, and ok flag
        """
        items = self.tree.selectedItems()
        if not items:
            QMessageBox.warning(self, "Warning", "No category selected")
            return None, "", False
            
        item = items[0]
        category_id = item.data(0, Qt.UserRole)
        old_name = item.text(0)
        
        name, ok = QInputDialog.getText(self, "Edit Category", 
                                     "Category name:", text=old_name)
        return category_id, name, ok

    def delete_category(self, item=None):
        """
        Delete the selected category
        
        Parameters
        ----------
        item : QTreeWidgetItem, optional
            Tree item to delete. If None, use the currently selected item.
        """
        if item is None:
            items = self.tree.selectedItems()
            if not items:
                QMessageBox.warning(self, "Warning", "No category selected")
                return
            item = items[0]
        
        category_id = item.data(0, Qt.UserRole)
        name = item.text(0)
        
        # Check if the category has subcategories
        has_children = item.childCount() > 0
        
        # Confirm deletion
        message = f"Are you sure you want to delete category '{name}'?"
        if has_children:
            message += "\nThis will also delete all subcategories!"
            
        reply = QMessageBox.question(self, "Confirm Deletion", message,
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # The presenter will handle this
            pass
            
    def get_delete_info(self):
        """Get category ID for deletion
        
        Returns
        -------
        tuple[int | None, bool]
            Category ID and ok flag
        """
        items = self.tree.selectedItems()
        if not items:
            QMessageBox.warning(self, "Warning", "No category selected")
            return None, False
            
        item = items[0]
        category_id = item.data(0, Qt.UserRole)
        name = item.text(0)
        
        # Check if the category has subcategories
        has_children = item.childCount() > 0
        
        # Confirm deletion
        message = f"Are you sure you want to delete category '{name}'?"
        if has_children:
            message += "\nThis will also delete all subcategories!"
            
        reply = QMessageBox.question(self, "Confirm Deletion", message,
                                    QMessageBox.Yes | QMessageBox.No)
        
        return category_id, reply == QMessageBox.Yes
