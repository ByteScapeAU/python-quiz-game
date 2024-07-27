import tkinter as tk  # Import tkinter for creating the GUI

from quiz_manager import QuizManager  # Import QuizManager to handle quiz logic
from user import User  # Import User to manage user details
from user_interface import UserInterface  # Import UserInterface to handle the GUI


def main():
    """
    Main function to initialize and run the quiz application.
    """
    # Create the main application window
    root = tk.Tk()
    root.title("Quiz Game")
    root.geometry("800x600")

    # Create instances of User and QuizManager
    user = User()
    quiz_manager = QuizManager("data/questions.json")

    # Initialize the UserInterface (ui) and assign it to root to avoid Flake8 warning
    root.ui = UserInterface(root, quiz_manager, user)

    # Start the tkinter main event loop
    root.mainloop()


if __name__ == "__main__":
    main()
