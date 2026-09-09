"""Question data loading and validation."""

import json
import logging
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from puzzlebox.models import Difficulty, Question

logger = logging.getLogger(__name__)


class QuestionLoadingError(Exception):
    """Raised when quiz questions cannot be loaded."""


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

    questions: list[QuestionData] = Field(min_length=1)


def load_questions(path: Path) -> tuple[Question, ...]:
    """Load and validate quiz questions from a JSON file."""
    logger.info("Loading questions from %s", path)

    try:
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
    except OSError as exc:
        raise QuestionLoadingError(f"Unable to read questions file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise QuestionLoadingError(f"Invalid JSON in questions file: {path}") from exc
    except ValidationError as exc:
        raise QuestionLoadingError(f"Invalid question data in: {path}") from exc
    except ValueError as exc:
        raise QuestionLoadingError(f"Invalid question data in: {path}") from exc

    logger.info("Loaded %d questions from %s", len(questions), path)

    return questions
