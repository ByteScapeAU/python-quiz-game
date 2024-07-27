import time  # Import time to handle timing functions
import tkinter as tk  # Import tkinter for creating the GUI
from io import BytesIO  # Import BytesIO for handling image data
from threading import Thread  # Import Thread for handling asynchronous tasks

import requests  # Import requests for downloading images
from PIL import Image, ImageTk, UnidentifiedImageError  # Import PIL for handling images


class UserInterface:
    """
    Class to manage the graphical user interface of the quiz application.
    """

    def __init__(self, root, quiz_manager, user):
        """
        Initialize the UserInterface with the root window, quiz manager, and user.
        """
        self.root = root  # The main tkinter window
        self.quiz_manager = quiz_manager  # Instance of QuizManager to handle quiz logic
        self.user = user  # Instance of User to store user details

        # Variable to store the selected option
        self.selected_option = tk.StringVar()
        self.selected_option.set(None)
        self.start_time = time.time()  # Track the start time of the quiz
        self.total_time = 0  # Total time taken for the quiz
        self.question_start_time = 0  # Track the start time of each question

        # Create frames for different parts of the GUI
        self.header_frame = tk.Frame(
            root
        )  # Frame for displaying user details and score
        self.quiz_frame = tk.Frame(root)  # Frame for displaying quiz questions
        self.button_frame = tk.Frame(
            root
        )  # Frame for action buttons (Submit, Next, Quit)

        self.create_user_details_frame()  # Create the initial frame for user details

    def create_user_details_frame(self):
        """
        Create the frame for entering user details (name and age).
        """
        self.user_details_frame = tk.Frame(self.root)

        # Label for entering details
        tk.Label(
            self.user_details_frame, text="Enter Your Details", font=("Arial", 24)
        ).grid(row=0, columnspan=2, pady=20)

        # Name label and entry
        tk.Label(self.user_details_frame, text="Name:").grid(
            row=1, column=0, pady=10, sticky=tk.W
        )
        self.name_entry = tk.Entry(self.user_details_frame)
        self.name_entry.grid(row=1, column=1, pady=10)

        # Age label and entry
        tk.Label(self.user_details_frame, text="Age:").grid(
            row=2, column=0, pady=10, sticky=tk.W
        )
        self.age_entry = tk.Entry(self.user_details_frame)
        self.age_entry.grid(row=2, column=1, pady=10)

        # Start quiz button
        tk.Button(
            self.user_details_frame, text="Start Quiz", command=self.start_quiz
        ).grid(row=4, columnspan=2, pady=20)

        # Feedback label for error messages
        self.feedback_label = tk.Label(
            self.user_details_frame, text="", font=("Arial", 12), fg="red"
        )
        self.feedback_label.grid(row=3, columnspan=2, pady=10)

        # Configure grid columns to expand equally
        self.user_details_frame.grid_columnconfigure(0, weight=1)
        self.user_details_frame.grid_columnconfigure(1, weight=1)

        # Pack the frame into the root window
        self.user_details_frame.pack(expand=True)

    def start_quiz(self):
        """
        Start the quiz after validating user details.
        """
        self.user.name = self.name_entry.get()
        self.user.age = self.age_entry.get()

        if not self.user.name or not self.user.age:
            self.feedback_label.config(text="Please enter all details")
            return

        try:
            self.user.age = int(self.user.age)
        except ValueError:
            self.feedback_label.config(text="Age must be a number")
            return

        self.user_details_frame.pack_forget()
        self.create_header_frame()
        self.create_quiz_frame()
        self.load_question()

    def create_header_frame(self):
        """
        Create the header frame to display user details, score, and time.
        """
        self.header_frame.pack(pady=10)
        tk.Label(
            self.header_frame, text=f"Name: {self.user.name}", font=("Arial", 14)
        ).grid(row=0, column=0, padx=20)
        tk.Label(
            self.header_frame, text=f"Age: {self.user.age}", font=("Arial", 14)
        ).grid(row=0, column=1, padx=20)
        self.score_label = tk.Label(
            self.header_frame,
            text=f"Score: {self.quiz_manager.score}/{self.quiz_manager.current_question_index}",
            font=("Arial", 14),
        )
        self.score_label.grid(row=0, column=2, padx=20)
        self.time_label = tk.Label(
            self.header_frame, text="Time: 0s", font=("Arial", 14)
        )
        self.time_label.grid(row=0, column=3, padx=20)
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=1)
        self.header_frame.grid_columnconfigure(2, weight=1)
        self.header_frame.grid_columnconfigure(3, weight=1)
        self.update_time()

    def create_quiz_frame(self):
        """
        Create the frame for displaying quiz questions and options.
        """
        self.quiz_frame.pack(pady=20, padx=20)

        self.image_label = tk.Label(self.quiz_frame)
        self.image_label.grid(row=0, columnspan=2, pady=10)

        self.question_label = tk.Label(
            self.quiz_frame, text="", font=("Arial", 18), wraplength=700
        )
        self.question_label.grid(row=1, columnspan=2, pady=10)

        self.options_frame = tk.Frame(self.quiz_frame)
        self.options_frame.grid(row=2, columnspan=2, pady=10)

        self.option_buttons = []
        for i in range(4):
            button = tk.Radiobutton(
                self.options_frame,
                text="",
                variable=self.selected_option,
                value=i,
                font=("Arial", 14),
                wraplength=300,
                indicatoron=0,
                width=20,
                height=2,
                relief=tk.RAISED,
                command=self.enable_submit_button,
            )
            button.grid(row=i // 2, column=i % 2, padx=10, pady=10)
            self.option_buttons.append(button)

        self.feedback_label = tk.Label(self.quiz_frame, text="", font=("Arial", 14))
        self.feedback_label.grid(row=3, columnspan=2, pady=0)

        self.create_button_frame()

    def create_button_frame(self):
        """
        Create the frame for action buttons (Submit, Next, Quit).
        """
        self.button_frame.pack(pady=10)
        self.submit_button = tk.Button(
            self.button_frame,
            text="Submit",
            command=self.submit_answer,
            state=tk.DISABLED,
        )
        self.submit_button.grid(row=0, column=0, padx=10)
        self.next_button = tk.Button(
            self.button_frame,
            text="Next Question",
            command=self.next_question,
            state=tk.DISABLED,
        )
        self.next_button.grid(row=0, column=1, padx=10)
        self.quit_button = tk.Button(
            self.button_frame, text="Quit", command=self.show_results
        )
        self.quit_button.grid(row=0, column=2, padx=10)
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)
        self.button_frame.grid_columnconfigure(2, weight=1)
        self.quiz_frame.pack_propagate(False)
        self.button_frame.pack_propagate(False)

    def load_question(self):
        """
        Load the current question and display it in the quiz frame.
        """
        self.selected_option.set(None)
        self.submit_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.DISABLED)
        self.feedback_label.config(text="")
        self.question_start_time = time.time()

        if not self.quiz_manager.is_quiz_over():
            question, options, self.correct_answer, image_path = (
                self.quiz_manager.get_randomized_question()
            )

            self.question_label.config(text=question)
            if image_path:
                thread = Thread(target=self.load_image, args=(image_path,))
                thread.start()
            else:
                self.image_label.grid_forget()

            for i, option in enumerate(options):
                self.option_buttons[i].config(text=option, state=tk.NORMAL)
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
            self.image = ImageTk.PhotoImage(image)
            self.image_label.config(image=self.image)
            self.image_label.grid(row=0, columnspan=2, pady=10)
        except (requests.exceptions.RequestException, UnidentifiedImageError) as e:
            print(f"Error loading image: {e}")
            self.image_label.grid_forget()

    def enable_submit_button(self):
        """
        Enable the Submit button when an option is selected.
        """
        self.submit_button.config(state=tk.NORMAL)

    def submit_answer(self):
        """
        Submit the selected answer and provide feedback.
        """
        selected_index = self.selected_option.get()
        selected_option = self.option_buttons[int(selected_index)].cget("text")
        if self.quiz_manager.check_answer(selected_option, self.correct_answer):
            self.feedback_label.config(text="Correct!", fg="green")
        else:
            self.feedback_label.config(
                text=f"Wrong! The correct answer was {self.correct_answer}", fg="red"
            )

        for button in self.option_buttons:
            button.config(state=tk.DISABLED)
        self.submit_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.NORMAL)

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
        self.score_label.config(
            text=f"Score: {self.quiz_manager.score}/{self.quiz_manager.current_question_index + 1}"
        )
        elapsed_time = int(time.time() - self.start_time)
        self.time_label.config(text=f"Time: {elapsed_time}s")

    def update_time(self):
        """
        Update the elapsed time every second.
        """
        if not self.quiz_manager.is_quiz_over():
            elapsed_time = int(time.time() - self.start_time)
            self.time_label.config(text=f"Time: {elapsed_time}s")
            self.root.after(1000, self.update_time)

    def show_results(self):
        """
        Show the quiz results when the quiz is over or the user quits.
        """
        if self.next_button["state"] == tk.NORMAL:
            self.quiz_manager.next_question()

        elapsed_time = time.time() - self.start_time
        average_time = (
            elapsed_time / self.quiz_manager.current_question_index
            if self.quiz_manager.current_question_index
            else 0
        )
        self.quiz_frame.pack_forget()
        self.button_frame.pack_forget()
        self.header_frame.pack_forget()

        result_frame = tk.Frame(self.root)
        result_frame.pack(pady=20)
        tk.Label(result_frame, text="Quiz Over!", font=("Arial", 24)).pack(pady=20)
        tk.Label(result_frame, text=f"Name: {self.user.name}").pack()
        tk.Label(result_frame, text=f"Age: {self.user.age}").pack()
        tk.Label(
            result_frame,
            text=f"Your Score: {self.quiz_manager.score}/{self.quiz_manager.current_question_index}",
            font=("Arial", 18),
        ).pack(pady=20)
        tk.Label(result_frame, text=f"Total Time: {int(elapsed_time)} seconds").pack(
            pady=10
        )
        tk.Label(
            result_frame, text=f"Average Time per Question: {average_time:.2f} seconds"
        ).pack(pady=10)
        tk.Button(result_frame, text="Close", command=self.root.quit).pack(pady=20)
