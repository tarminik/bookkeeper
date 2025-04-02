"""
Application entry point for the Bookkeeper GUI
"""

import sys
import os
from PyQt5.QtWidgets import QApplication

from bookkeeper.view.main_window import MainWindow
from bookkeeper.presenter import BookkeeperPresenter


def run_app():
    """Run the Bookkeeper application"""
    app = QApplication(sys.argv)
    
    # Create main window
    window = MainWindow()
    
    # Get database path
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data.db')
    
    # Create presenter to connect view with model
    presenter = BookkeeperPresenter(db_path, window)
    
    # Show window
    window.show()
    
    # Start event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_app()
