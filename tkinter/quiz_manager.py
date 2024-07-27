import json  # Import json to handle JSON files
import random  # Import random to shuffle quiz options


class QuizManager:
    """
    Class to manage quiz logic, including loading questions, shuffling options,
    and checking answers.
    """

    def __init__(self, question_file):
        """
        Initialize the QuizManager with the path to the question file.
        """
        self.questions = self.load_questions(question_file)
        self.current_question_index = 0
        self.score = 0

    def load_questions(self, file_path):
        """
        Load questions from a JSON file.
        """
        try:
            with open(file_path, "r") as file:
                questions = json.load(file)
            return questions
        except FileNotFoundError:
            print(f"Error: The file {file_path} was not found.")
            return []
        except json.JSONDecodeError:
            print(f"Error: The file {file_path} contains invalid JSON.")
            return []

    def get_randomized_question(self):
        """
        Retrieve the current question with options in random order.
        """
        if self.current_question_index < len(self.questions):
            question_data = self.questions[self.current_question_index]
            question = question_data["question"]
            options = question_data["options"]
            random.shuffle(options)
            correct = question_data["correct"]
            image = question_data.get("image", "")
            return question, options, correct, image
        else:
            return None, None, None, None

    def next_question(self):
        """
        Move to the next question.
        """
        self.current_question_index += 1

    def check_answer(self, selected_option, correct_option):
        """
        Check if the selected option is correct and update the score.
        """
        if selected_option == correct_option:
            self.score += 1
            return True
        else:
            return False

    def is_quiz_over(self):
        """
        Check if all questions have been answered.
        """
        return self.current_question_index >= len(self.questions)
