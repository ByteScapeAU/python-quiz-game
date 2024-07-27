import sys  # Import sys to handle system-specific parameters and functions

from PyQt6.QtWidgets import QApplication
from quiz_manager import QuizManager
from user import User
from user_interface import UserInterface


def main():
    app = QApplication(sys.argv)  # Create the application instance
    quiz_manager = QuizManager("data/questions.json")  # Initialize the quiz manager
    user = User()  # Initialize the user instance
    ui = UserInterface(quiz_manager, user)  # Create the user interface
    ui.show()  # Show the user interface
    sys.exit(app.exec())  # Execute the application


if __name__ == "__main__":
    main()  # Run the main function
