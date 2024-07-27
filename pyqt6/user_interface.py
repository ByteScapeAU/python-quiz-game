import time  # Import time to handle timing functions
from io import BytesIO  # Import BytesIO for handling image data
from threading import (  # Import Thread and Lock for handling asynchronous tasks
    Lock,
    Thread,
)

import requests  # Import requests for downloading images
from PIL import Image, ImageQt, UnidentifiedImageError  # Import PIL for handling images
from PyQt6.QtCore import QObject, Qt, QTimer, pyqtSignal  # Import PyQt6 modules
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import (
    QButtonGroup,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)


class SignalEmitter(QObject):
    image_loaded = pyqtSignal(QPixmap)


class UserInterface(QWidget):
    """
    Class to manage the graphical user interface of the quiz application.
    """

    def __init__(self, quiz_manager, user):
        """
        Initialize the UserInterface with the root window, quiz manager, and user.
        """
        super().__init__()

        self.quiz_manager = quiz_manager  # Instance of QuizManager to handle quiz logic
        self.user = user  # Instance of User to store user details

        self.selected_option = None  # Variable to store the selected option
        self.start_time = time.time()  # Track the start time of the quiz
        self.total_time = 0  # Total time taken for the quiz
        self.question_start_time = 0  # Track the start time of each question

        self.layout = QVBoxLayout(self)  # Main layout of the widget
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.header_frame_widget = QWidget()
        self.quiz_frame_widget = QWidget()
        self.button_frame_widget = QWidget()

        self.signal_emitter = SignalEmitter()
        self.signal_emitter.image_loaded.connect(self.display_image)
        self.lock = Lock()

        self.create_user_details_frame()  # Create the initial frame for user details

    def create_user_details_frame(self):
        """
        Create the frame for entering user details (name and age).
        """
        self.user_details_frame_widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(
            QLabel(
                "Enter Your Details",
                alignment=Qt.AlignmentFlag.AlignCenter,
                font=QFont("Arial", 24),
            )
        )

        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_entry = QLineEdit()
        name_layout.addWidget(self.name_entry)
        layout.addLayout(name_layout)

        age_layout = QHBoxLayout()
        age_layout.addWidget(QLabel("Age:"))
        self.age_entry = QLineEdit()
        age_layout.addWidget(self.age_entry)
        layout.addLayout(age_layout)

        start_button = QPushButton("Start Quiz")
        start_button.clicked.connect(self.start_quiz)
        layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.feedback_label = QLabel("", alignment=Qt.AlignmentFlag.AlignCenter)
        self.feedback_label.setStyleSheet("color: red;")
        layout.addWidget(self.feedback_label)

        self.user_details_frame_widget.setLayout(layout)
        self.layout.addWidget(self.user_details_frame_widget)

    def start_quiz(self):
        """
        Start the quiz after validating user details.
        """
        self.user.name = self.name_entry.text()
        self.user.age = self.age_entry.text()

        if not self.user.name or not self.user.age:
            self.feedback_label.setText("Please enter all details")
            return

        try:
            self.user.age = int(self.user.age)
        except ValueError:
            self.feedback_label.setText("Age must be a number")
            return

        self.user_details_frame_widget.hide()
        self.create_header_frame()
        self.create_quiz_frame()
        self.load_question()

    def create_header_frame(self):
        """
        Create the header frame to display user details, score, and time.
        """
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel(f"Name: {self.user.name}"))
        header_layout.addWidget(QLabel(f"Age: {self.user.age}"))
        self.score_label = QLabel(
            f"Score: {self.quiz_manager.score}/{self.quiz_manager.current_question_index}",
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
        header_layout.addWidget(self.score_label)
        self.time_label = QLabel("Time: 0s", alignment=Qt.AlignmentFlag.AlignRight)
        self.time_label.setFixedWidth(100)  # Set fixed width for the time label
        header_layout.addWidget(self.time_label)

        self.header_frame_widget.setLayout(header_layout)
        self.layout.addWidget(self.header_frame_widget)
        self.update_time()

    def create_quiz_frame(self):
        """
        Create the frame for displaying quiz questions and options.
        """
        quiz_layout = QVBoxLayout()

        self.image_label = QLabel()
        quiz_layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.question_label = QLabel(
            "", alignment=Qt.AlignmentFlag.AlignCenter, font=QFont("Arial", 18)
        )
        quiz_layout.addWidget(
            self.question_label, alignment=Qt.AlignmentFlag.AlignCenter
        )

        options_layout = QGridLayout()
        self.option_buttons = []
        self.button_group = QButtonGroup()
        for i in range(4):
            button = QRadioButton()
            button.toggled.connect(self.enable_submit_button)
            options_layout.addWidget(button, i // 2, i % 2)
            self.option_buttons.append(button)
            self.button_group.addButton(button)

        quiz_layout.addLayout(options_layout)

        self.feedback_label = QLabel("", alignment=Qt.AlignmentFlag.AlignCenter)
        quiz_layout.addWidget(self.feedback_label)

        self.quiz_frame_widget.setLayout(quiz_layout)
        self.layout.addWidget(self.quiz_frame_widget)

        self.create_button_frame()

    def create_button_frame(self):
        """
        Create the frame for action buttons (Submit, Next, Quit).
        """
        button_layout = QHBoxLayout()
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_answer)
        self.submit_button.setEnabled(False)
        button_layout.addWidget(self.submit_button)

        self.next_button = QPushButton("Next Question")
        self.next_button.clicked.connect(self.next_question)
        self.next_button.setEnabled(False)
        button_layout.addWidget(self.next_button)

        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.show_results)
        button_layout.addWidget(self.quit_button)

        self.button_frame_widget.setLayout(button_layout)
        self.layout.addWidget(self.button_frame_widget)

    def load_question(self):
        """
        Load the current question and display it in the quiz frame.
        """
        self.selected_option = None
        self.submit_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.feedback_label.setText("")
        self.question_start_time = time.time()

        if not self.quiz_manager.is_quiz_over():
            question, options, self.correct_answer, image_path = (
                self.quiz_manager.get_randomized_question()
            )

            self.question_label.setText(question)
            if image_path:
                thread = Thread(target=self.load_image, args=(image_path,))
                thread.start()
            else:
                self.image_label.clear()

            self.button_group.setExclusive(False)
            for button in self.option_buttons:
                button.setChecked(False)
                button.setEnabled(True)
            self.button_group.setExclusive(True)

            for i, option in enumerate(options):
                self.option_buttons[i].setText(option)
        else:
            self.show_results()

    def load_image(self, image_path):
        """
        Load an image from a URL or file path and display it.
        """
        try:
            if image_path.startswith("http"):
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
                }
                response = requests.get(image_path, headers=headers)
                response.raise_for_status()
                img_data = response.content
                image = Image.open(BytesIO(img_data))
            else:
                image = Image.open(image_path)
            image = image.resize((200, 200), Image.LANCZOS)
            pixmap = QPixmap.fromImage(ImageQt.ImageQt(image))
            self.signal_emitter.image_loaded.emit(pixmap)
        except (requests.exceptions.RequestException, UnidentifiedImageError) as e:
            print(f"Error loading image: {e}")
            self.image_label.clear()

    def display_image(self, pixmap):
        """
        Display the image on the label.
        """
        with self.lock:
            self.image_label.setPixmap(pixmap)

    def enable_submit_button(self):
        """
        Enable the Submit button when an option is selected.
        """
        if self.button_group.checkedButton() is not None:
            self.submit_button.setEnabled(True)

    def submit_answer(self):
        """
        Submit the selected answer and provide feedback.
        """
        selected_button = self.button_group.checkedButton()
        if selected_button:
            selected_option = selected_button.text()
            if self.quiz_manager.check_answer(selected_option, self.correct_answer):
                self.feedback_label.setText("Correct!")
                self.feedback_label.setStyleSheet("color: green;")
            else:
                self.feedback_label.setText(
                    f"Wrong! The correct answer was {self.correct_answer}"
                )
                self.feedback_label.setStyleSheet("color: red;")

            for button in self.option_buttons:
                button.setEnabled(False)
            self.submit_button.setEnabled(False)
            self.next_button.setEnabled(True)

            self.total_time += time.time() - self.question_start_time
            self.update_score()

    def next_question(self):
        """
        Load the next question.
        """
        self.quiz_manager.next_question()
        self.load_question()

    def update_score(self):
        """
        Update the score and time labels.
        """
        self.score_label.setText(
            f"Score: {self.quiz_manager.score}/{self.quiz_manager.current_question_index + 1}"
        )
        elapsed_time = int(time.time() - self.start_time)
        self.time_label.setText(f"Time: {elapsed_time}s")

    def update_time(self):
        """
        Update the elapsed time every second.
        """
        if not self.quiz_manager.is_quiz_over():
            elapsed_time = int(time.time() - self.start_time)
            self.time_label.setText(f"Time: {elapsed_time}s")
            QTimer.singleShot(1000, self.update_time)

    def show_results(self):
        """
        Show the quiz results when the quiz is over or the user quits.
        """
        # Hide the buttons and header when showing results
        self.submit_button.hide()
        self.next_button.hide()
        self.quit_button.hide()
        self.header_frame_widget.hide()

        # If the quiz is not over but the user quits after submitting an answer, ensure the question index is incremented
        if self.next_button.isEnabled():
            self.quiz_manager.next_question()

        elapsed_time = time.time() - self.start_time
        average_time = (
            elapsed_time / self.quiz_manager.current_question_index
            if self.quiz_manager.current_question_index
            else 0
        )
        self.quiz_frame_widget.hide()
        self.button_frame_widget.hide()

        result_frame = QWidget()
        result_layout = QVBoxLayout()

        result_layout.addWidget(
            QLabel(
                "Quiz Over!",
                alignment=Qt.AlignmentFlag.AlignCenter,
                font=QFont("Arial", 24),
            )
        )
        result_layout.addWidget(
            QLabel(f"Name: {self.user.name}", alignment=Qt.AlignmentFlag.AlignCenter)
        )
        result_layout.addWidget(
            QLabel(f"Age: {self.user.age}", alignment=Qt.AlignmentFlag.AlignCenter)
        )
        result_layout.addWidget(
            QLabel(
                f"Your Score: {self.quiz_manager.score}/{self.quiz_manager.current_question_index}",
                alignment=Qt.AlignmentFlag.AlignCenter,
                font=QFont("Arial", 18),
            )
        )
        result_layout.addWidget(
            QLabel(
                f"Total Time: {int(elapsed_time)} seconds",
                alignment=Qt.AlignmentFlag.AlignCenter,
            )
        )
        result_layout.addWidget(
            QLabel(
                f"Average Time per Question: {average_time:.2f} seconds",
                alignment=Qt.AlignmentFlag.AlignCenter,
            )
        )

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        result_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)

        result_frame.setLayout(result_layout)
        self.layout.addWidget(result_frame)
