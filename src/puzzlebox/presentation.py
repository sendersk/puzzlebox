"""Presentation helpers for the PuzzleBox CLI."""

from puzzlebox.runner import QuizRunner


def display_question(runner: QuizRunner) -> None:
    """Display the current question."""
    question = runner.current_question

    print()
    print(f"Question {question.number}/{question.total}")
    print()
    print(question.text)
    print()

    for number, answer in enumerate(question.answers, start=1):
        print(f"{number}. {answer}")


def get_answer(runner: QuizRunner) -> int:
    """Read an answer number from the user."""
    while True:
        value = input("Your answer: ")

        try:
            answer_number = int(value)
        except ValueError:
            print("Please enter a number.")
            continue

        if 1 <= answer_number <= len(runner.current_question.answers):
            return answer_number

        print("Please select one of the available answers.")
