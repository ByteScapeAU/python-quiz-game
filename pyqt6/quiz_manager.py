import json
import random


class QuizManager:
    def __init__(self, question_file):
        self.questions = self.load_questions(question_file)  # Load questions from file
        self.current_question_index = 0  # Start with the first question
        self.score = 0  # Initialize score

    def load_questions(self, file_path):
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
        if self.current_question_index < len(self.questions):
            question_data = self.questions[self.current_question_index]
            question = question_data["question"]
            options = question_data["options"]
            random.shuffle(options)  # Randomize options
            correct = question_data["correct"]
            image = question_data.get("image", "")
            return question, options, correct, image
        else:
            return None, None, None, None

    def next_question(self):
        self.current_question_index += 1  # Move to the next question

    def check_answer(self, selected_option, correct_option):
        if selected_option == correct_option:
            self.score += 1  # Increase score for correct answer
            return True
        else:
            return False

    def is_quiz_over(self):
        return self.current_question_index >= len(
            self.questions
        )  # Check if quiz is over
