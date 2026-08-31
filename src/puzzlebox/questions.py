"""Question data loading and validation."""

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from puzzlebox.models import Difficulty, Question


class QuestionData(BaseModel):
    """Represent validated question data from an external source."""

    model_config = ConfigDict(extra="forbid")

    text: str
    answers: list[str]
    correct_answer: str
    category: str
    difficulty: Difficulty


class QuestionCollection(BaseModel):
    """Represent a collection of question data."""

    model_config = ConfigDict(extra="forbid")

    questions: list[QuestionData]


def load_questions(path: Path) -> tuple[Question, ...]:
    """Load and validate questions from a JSON file."""
    data = json.loads(path.read_text(encoding="utf-8"))
    collection = QuestionCollection.model_validate(data)

    return tuple(
        Question(
            text=question.text,
            answers=tuple(question.answers),
            correct_answer=question.correct_answer,
            category=question.category,
            difficulty=question.difficulty,
        )
        for question in collection.questions
    )
