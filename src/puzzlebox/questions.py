"""Question data loading and validation."""

import json
import logging
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from puzzlebox.models import Difficulty, Question

logger = logging.getLogger(__name__)


class QuestionData(BaseModel):
    """Validated question data loaded from JSON."""

    model_config = ConfigDict(extra="forbid")

    text: str
    answers: list[str]
    correct_answer: str
    category: str
    difficulty: Difficulty


class QuestionCollection(BaseModel):
    """Collection of validated question data."""

    model_config = ConfigDict(extra="forbid")

    questions: list[QuestionData]


def load_questions(path: Path) -> tuple[Question, ...]:
    """Load and validate quiz questions from a JSON file."""
    logger.info("Loading questions from %s", path)

    content = path.read_text(encoding="utf-8")
    data = json.loads(content)
    collection = QuestionCollection.model_validate(data)

    questions = tuple(
        Question(
            text=item.text,
            answers=tuple(item.answers),
            correct_answer=item.correct_answer,
            category=item.category,
            difficulty=item.difficulty,
        )
        for item in collection.questions
    )

    logger.info("Loaded %d questions from %s", len(questions), path)

    return questions
