"""Tests for the command-line interface."""

from importlib.metadata import version
from pathlib import Path
from unittest.mock import Mock

import pytest
import typer
from typer.testing import CliRunner

from puzzlebox.cli import (
    answer_question,
    app,
    create_runner,
    move_to_next_question,
    run_quiz,
)
from puzzlebox.config import AppConfig, ConfigurationError
from puzzlebox.models import Difficulty, Question, Quiz, QuizSession
from puzzlebox.questions import QuestionLoadingError
from puzzlebox.repositories import JsonQuestionRepository
from puzzlebox.runner import QuizRunner

runner = CliRunner()


def test_run_quiz_with_user_input(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    """Test running a complete quiz from the command line."""
    questions_file = tmp_path / "questions.json"

    questions_file.write_text(
        """
        {
            "questions": [
                {
                    "text": "What is 2 + 2?",
                    "answers": ["3", "4"],
                    "correct_answer": "4",
                    "category": "Math",
                    "difficulty": "easy"
                }
            ]
        }
        """,
        encoding="utf-8",
    )

    monkeypatch.setattr("builtins.input", lambda _: "2")

    run_quiz(questions_file)

    output = capsys.readouterr().out

    assert "PuzzleBox" in output
    assert "What is 2 + 2?" in output
    assert "Correct!" in output
    assert "Score: 1/1" in output
    assert "Percentage: 100.0%" in output


def test_cli_help() -> None:
    """Test that the CLI exposes the help message."""
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "--questions" in result.stdout
    assert "-q" in result.stdout


def test_cli_accepts_questions_option(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Test that the CLI passes the question path to the quiz runner."""
    questions_path = tmp_path / "questions.json"
    questions_path.write_text("[]", encoding="utf-8")

    called_with: dict[str, object] = {}

    def fake_run_quiz(
        path: Path,
        *,
        category: str | None = None,
        shuffle_questions: bool = False,
    ) -> None:
        called_with["path"] = path
        called_with["shuffle_questions"] = shuffle_questions

    monkeypatch.setattr("puzzlebox.cli.run_quiz", fake_run_quiz)

    result = runner.invoke(
        app,
        ["--questions", str(questions_path)],
    )

    assert result.exit_code == 0
    assert called_with["path"] == questions_path
    assert called_with["shuffle_questions"] is False


def test_cli_accepts_short_questions_option(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Test that the CLI accepts the short questions option."""
    questions_path = tmp_path / "questions.json"
    questions_path.write_text("[]", encoding="utf-8")

    called_with: dict[str, object] = {}

    def fake_run_quiz(
        path: Path,
        *,
        category: str | None = None,
        shuffle_questions: bool = False,
    ) -> None:
        called_with["path"] = path
        called_with["shuffle_questions"] = shuffle_questions

    monkeypatch.setattr("puzzlebox.cli.run_quiz", fake_run_quiz)

    result = runner.invoke(
        app,
        ["-q", str(questions_path)],
    )

    assert result.exit_code == 0
    assert called_with["path"] == questions_path
    assert called_with["shuffle_questions"] is False


def test_cli_rejects_missing_questions_file(tmp_path: Path) -> None:
    """Test that the CLI rejects a missing question file."""
    questions_path = tmp_path / "missing.json"

    result = runner.invoke(
        app,
        ["--questions", str(questions_path)],
    )

    assert result.exit_code == 2
    assert "does not exist" in result.stderr


def test_cli_uses_configured_questions_path(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Test that the CLI uses the configured questions path by default."""
    questions_path = tmp_path / "questions.json"
    questions_path.write_text("[]", encoding="utf-8")

    called_with: dict[str, object] = {}

    def fake_run_quiz(
        path: Path,
        *,
        category: str | None = None,
        shuffle_questions: bool = False,
    ) -> None:
        called_with["path"] = path
        called_with["shuffle_questions"] = shuffle_questions

    monkeypatch.setattr("puzzlebox.cli.run_quiz", fake_run_quiz)
    monkeypatch.setattr(
        "puzzlebox.cli.load_config",
        lambda _: AppConfig(questions_path=questions_path),
    )

    result = runner.invoke(app, [])

    assert result.exit_code == 0
    assert called_with["path"] == questions_path
    assert called_with["shuffle_questions"] is False


def test_cli_option_overrides_config(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Test that the CLI option overrides the configured questions path."""
    configured_path = tmp_path / "configured.json"
    cli_path = tmp_path / "cli.json"

    configured_path.write_text("[]", encoding="utf-8")
    cli_path.write_text("[]", encoding="utf-8")

    called_with: dict[str, object] = {}

    def fake_run_quiz(
        path: Path,
        *,
        category: str | None = None,
        shuffle_questions: bool = False,
    ) -> None:
        called_with["path"] = path
        called_with["shuffle_questions"] = shuffle_questions

    monkeypatch.setattr("puzzlebox.cli.run_quiz", fake_run_quiz)
    monkeypatch.setattr(
        "puzzlebox.cli.load_config",
        lambda _: AppConfig(questions_path=configured_path),
    )

    result = runner.invoke(
        app,
        ["--questions", str(cli_path)],
    )

    assert result.exit_code == 0
    assert called_with["path"] == cli_path
    assert called_with["shuffle_questions"] is False


def test_cli_reports_configuration_error(monkeypatch) -> None:
    """Test that configuration errors are reported to the user."""

    def fake_load_config(_: Path) -> None:
        raise ConfigurationError("Invalid configuration data.")

    monkeypatch.setattr(
        "puzzlebox.cli.load_config",
        fake_load_config,
    )

    result = runner.invoke(app, [])

    assert result.exit_code == 1
    assert "Error: Invalid configuration data." in result.stderr


def test_cli_does_not_start_quiz_when_configuration_fails(
    monkeypatch,
) -> None:
    """Test that the quiz is not started after a configuration error."""
    called = False

    def fake_load_config(_: Path) -> None:
        raise ConfigurationError("Configuration failed.")

    def fake_run_quiz(_: Path) -> None:
        nonlocal called
        called = True

    monkeypatch.setattr(
        "puzzlebox.cli.load_config",
        fake_load_config,
    )
    monkeypatch.setattr(
        "puzzlebox.cli.run_quiz",
        fake_run_quiz,
    )

    result = runner.invoke(app, [])

    assert result.exit_code == 1
    assert called is False


def test_run_quiz_reports_question_loading_error(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Test that question loading errors are reported by the CLI."""
    questions_file = tmp_path / "questions.json"
    questions_file.write_text("{}", encoding="utf-8")

    def raise_loading_error(
        path: Path,
    ) -> tuple:
        raise QuestionLoadingError("Invalid question data.")

    monkeypatch.setattr(
        "puzzlebox.cli.JsonQuestionRepository.get_questions",
        raise_loading_error,
    )

    result = runner.invoke(
        app,
        ["--questions", str(questions_file)],
    )

    assert result.exit_code == 1
    assert "Error: Invalid question data." in result.stderr


def test_cli_reports_invalid_configured_questions_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Test that an invalid configured questions file is reported."""
    questions_file = tmp_path / "questions.json"
    questions_file.write_text("{ invalid json", encoding="utf-8")

    monkeypatch.setattr(
        "puzzlebox.cli.load_config",
        lambda path: AppConfig(questions_path=questions_file),
    )

    result = runner.invoke(app)

    assert result.exit_code == 1
    assert "Error: Invalid JSON in questions file" in result.stderr


def test_run_quiz_does_not_hide_unexpected_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Test that unexpected errors are not hidden by the CLI."""
    questions_file = tmp_path / "questions.json"
    questions_file.write_text("{}", encoding="utf-8")

    def raise_unexpected_error(
        repository: JsonQuestionRepository,
    ) -> tuple:
        raise RuntimeError("Unexpected application error.")

    monkeypatch.setattr(
        "puzzlebox.cli.JsonQuestionRepository.get_questions",
        raise_unexpected_error,
    )

    with pytest.raises(RuntimeError, match="Unexpected application error"):
        run_quiz(questions_file)


def test_run_quiz_displays_final_score(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test that the CLI displays the final quiz score."""
    questions_file = tmp_path / "questions.json"

    questions_file.write_text(
        """
        {
            "questions": [
                {
                    "text": "What is 2 + 2?",
                    "answers": ["3", "4"],
                    "correct_answer": "4",
                    "category": "Math",
                    "difficulty": "easy"
                }
            ]
        }
        """,
        encoding="utf-8",
    )

    monkeypatch.setattr("builtins.input", lambda _: "2")

    run_quiz(questions_file)

    captured = capsys.readouterr()

    assert "Quiz finished!" in captured.out
    assert "Score: 1/1" in captured.out
    assert "Percentage: 100.0%" in captured.out


def test_create_runner_creates_quiz_runner(tmp_path) -> None:
    """Test that create_runner creates a runner from a questions file."""
    questions_path = tmp_path / "questions.json"
    questions_path.write_text(
        """
        {
            "questions": [
                {
                    "text": "What is 2 + 2?",
                    "answers": ["3", "4"],
                    "correct_answer": "4",
                    "category": "Math",
                    "difficulty": "easy"
                }
            ]
        }
        """,
        encoding="utf-8",
    )

    runner = create_runner(questions_path)

    assert isinstance(runner, QuizRunner)
    assert runner.total_questions == 1
    assert runner.current_question.text == "What is 2 + 2?"


def test_answer_question_returns_correct_result(monkeypatch) -> None:
    """Test that answer_question returns the result of the submitted answer."""
    question = Question(
        text="What is 2 + 2?",
        answers=("3", "4"),
        correct_answer="4",
        category="Math",
        difficulty=Difficulty.EASY,
    )
    quiz = Quiz(questions=(question,))
    runner = QuizRunner(QuizSession(quiz))

    monkeypatch.setattr("builtins.input", lambda _: "2")

    result = answer_question(runner)

    assert result is True
    assert runner.score == 1


def test_move_to_next_question_advances_runner() -> None:
    """Test that move_to_next_question advances an unfinished quiz."""
    questions = (
        Question(
            text="Question 1",
            answers=("A", "B"),
            correct_answer="A",
            category="Test",
            difficulty=Difficulty.EASY,
        ),
        Question(
            text="Question 2",
            answers=("C", "D"),
            correct_answer="C",
            category="Test",
            difficulty=Difficulty.EASY,
        ),
    )
    quiz = Quiz(questions=questions)
    runner = QuizRunner(QuizSession(quiz))

    move_to_next_question(runner)

    assert runner.current_question.text == "Question 2"


def test_move_to_next_question_does_not_advance_finished_quiz() -> None:
    """Test that move_to_next_question does nothing after the quiz is finished."""
    question = Question(
        text="Question",
        answers=("A", "B"),
        correct_answer="A",
        category="Test",
        difficulty=Difficulty.EASY,
    )
    quiz = Quiz(questions=(question,))
    runner = QuizRunner(QuizSession(quiz))

    runner.answer("A")
    move_to_next_question(runner)

    assert runner.is_finished is True
    assert runner.current_question.text == "Question"


def test_run_quiz_handles_keyboard_interrupt(monkeypatch, capsys, tmp_path) -> None:
    """Test that Ctrl+C cancels the quiz gracefully."""
    question = Question(
        text="What is 2 + 2?",
        answers=("3", "4"),
        correct_answer="4",
        category="Math",
        difficulty=Difficulty.EASY,
    )
    quiz = Quiz(questions=(question,))
    runner = QuizRunner(QuizSession(quiz))

    monkeypatch.setattr(
        "puzzlebox.cli.create_runner",
        lambda _, category=None, shuffle_questions=False: runner,
    )

    def interrupt(_runner: QuizRunner) -> None:
        raise KeyboardInterrupt

    monkeypatch.setattr(
        "puzzlebox.cli.process_question",
        interrupt,
    )

    run_quiz(tmp_path / "questions.json")

    captured = capsys.readouterr()

    assert captured.out == ("PuzzleBox\n=========\n\nQuiz cancelled.\n")


def test_run_quiz_handles_eof_error(monkeypatch, capsys, tmp_path) -> None:
    """Test that closed input cancels the quiz without an error."""
    question = Question(
        text="What is 2 + 2?",
        answers=("3", "4"),
        correct_answer="4",
        category="Math",
        difficulty=Difficulty.EASY,
    )
    quiz = Quiz(questions=(question,))
    runner = QuizRunner(QuizSession(quiz))

    monkeypatch.setattr(
        "puzzlebox.cli.create_runner",
        lambda _, category=None, shuffle_questions=False: runner,
    )

    def raise_eof(_runner: QuizRunner) -> bool:
        raise EOFError

    monkeypatch.setattr(
        "puzzlebox.cli.process_question",
        raise_eof,
    )

    run_quiz(tmp_path / "questions.json")

    captured = capsys.readouterr()

    assert captured.out == ("PuzzleBox\n=========\n\nQuiz cancelled.\n")


def test_cli_version() -> None:
    """Test that the CLI displays the application version."""
    runner = typer.testing.CliRunner()

    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout == f"PuzzleBox {version('puzzlebox')}\n"


def test_cli_version_does_not_load_config(monkeypatch) -> None:
    """Test that the version option skips normal application startup."""
    runner = typer.testing.CliRunner()

    def fail_if_called(*args, **kwargs):
        raise AssertionError("load_config should not be called")

    monkeypatch.setattr("puzzlebox.cli.load_config", fail_if_called)

    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout.startswith("PuzzleBox ")


def test_cli_version_does_not_run_quiz(monkeypatch) -> None:
    """Test that the version option does not start the quiz."""
    runner = typer.testing.CliRunner()

    def fail_if_called(*args, **kwargs):
        raise AssertionError("run_quiz should not be called")

    monkeypatch.setattr("puzzlebox.cli.run_quiz", fail_if_called)

    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout.startswith("PuzzleBox ")


def test_cli_passes_shuffle_configuration_to_run_quiz(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Test that the CLI passes shuffle configuration to the quiz runner."""
    questions_path = tmp_path / "questions.json"
    questions_path.write_text("[]", encoding="utf-8")

    called_with: dict[str, object] = {}

    def fake_run_quiz(
        path: Path,
        *,
        category: str | None = None,
        shuffle_questions: bool = False,
    ) -> None:
        called_with["path"] = path
        called_with["shuffle_questions"] = shuffle_questions

    monkeypatch.setattr("puzzlebox.cli.run_quiz", fake_run_quiz)
    monkeypatch.setattr(
        "puzzlebox.cli.load_config",
        lambda _: AppConfig(
            questions_path=questions_path,
            shuffle_questions=True,
        ),
    )

    result = runner.invoke(app, [])

    assert result.exit_code == 0
    assert called_with["path"] == questions_path
    assert called_with["shuffle_questions"] is True


def test_create_runner_passes_shuffle_configuration_to_create_quiz(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Test that create_runner passes shuffle configuration to quiz creation."""
    questions_path = tmp_path / "questions.json"
    questions_path.write_text(
        """
{
    "questions": [
        {
            "text": "Question 1",
            "answers": ["A", "B"],
            "correct_answer": "A",
            "category": "Test",
            "difficulty": "easy"
        }
    ]
}
""".strip(),
        encoding="utf-8",
    )

    called_with: dict[str, object] = {}

    def fake_create_quiz(
            repository,
            *,
            category: str | None = None,
            shuffle: bool = False,
    ) -> Quiz:
        called_with["repository"] = repository
        called_with["shuffle"] = shuffle

        return Quiz(
            questions=(
                Question(
                    text="Test question",
                    answers=("A", "B"),
                    correct_answer="A",
                    category="Test",
                    difficulty=Difficulty.EASY,
                ),
            ),
        )

    monkeypatch.setattr(
        "puzzlebox.cli.create_quiz",
        fake_create_quiz,
    )

    runner = create_runner(
        questions_path,
        shuffle_questions=True,
    )

    assert isinstance(runner, QuizRunner)
    assert called_with["shuffle"] is True


def test_run_quiz_uses_shuffled_questions_when_enabled(
    monkeypatch,
    capsys,
    tmp_path: Path,
) -> None:
    """Test that run_quiz uses shuffled questions when enabled."""
    questions_path = tmp_path / "questions.json"
    questions_path.write_text(
        """
{
    "questions": [
        {
            "text": "Question 1",
            "answers": ["A", "B"],
            "correct_answer": "A",
            "category": "Test",
            "difficulty": "easy"
        },
        {
            "text": "Question 2",
            "answers": ["A", "B"],
            "correct_answer": "B",
            "category": "Test",
            "difficulty": "easy"
        }
    ]
}
""".strip(),
        encoding="utf-8",
    )

    question_one = Question(
        text="Question 1",
        answers=("A", "B"),
        correct_answer="A",
        category="Test",
        difficulty=Difficulty.EASY,
    )
    question_two = Question(
        text="Question 2",
        answers=("A", "B"),
        correct_answer="B",
        category="Test",
        difficulty=Difficulty.EASY,
    )

    questions = (question_one, question_two)

    def fake_shuffle(
        questions_to_shuffle: tuple[Question, ...],
    ) -> tuple[Question, ...]:
        return tuple(reversed(questions_to_shuffle))

    monkeypatch.setattr(
        "puzzlebox.quiz.shuffle_questions",
        fake_shuffle,
    )

    answers = iter(["2", "1"])

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(answers),
    )

    run_quiz(
        questions_path,
        shuffle_questions=True,
    )

    captured = capsys.readouterr()

    assert "Question 1/2" in captured.out
    assert "Question 2/2" in captured.out
    assert "Score: 2/2" in captured.out


def test_cli_uses_configured_shuffle_value_when_option_is_not_provided(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Test that CLI uses the configured shuffle value by default."""
    questions_path = tmp_path / "questions.json"
    questions_path.write_text("[]", encoding="utf-8")

    called_with: dict[str, object] = {}

    def fake_run_quiz(
        path: Path,
        *,
        category: str | None = None,
        shuffle_questions: bool = False,
    ) -> None:
        called_with["path"] = path
        called_with["shuffle_questions"] = shuffle_questions

    monkeypatch.setattr("puzzlebox.cli.run_quiz", fake_run_quiz)
    monkeypatch.setattr(
        "puzzlebox.cli.load_config",
        lambda _: AppConfig(
            questions_path=questions_path,
            shuffle_questions=True,
        ),
    )

    result = runner.invoke(app, [])

    assert result.exit_code == 0
    assert called_with["path"] == questions_path
    assert called_with["shuffle_questions"] is True


def test_cli_shuffle_option_overrides_disabled_configuration(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Test that CLI shuffle option overrides disabled configuration."""
    questions_path = tmp_path / "questions.json"
    questions_path.write_text("[]", encoding="utf-8")

    called_with: dict[str, object] = {}

    def fake_run_quiz(
        path: Path,
        *,
        category: str | None = None,
        shuffle_questions: bool = False,
    ) -> None:
        called_with["path"] = path
        called_with["shuffle_questions"] = shuffle_questions

    monkeypatch.setattr("puzzlebox.cli.run_quiz", fake_run_quiz)
    monkeypatch.setattr(
        "puzzlebox.cli.load_config",
        lambda _: AppConfig(
            questions_path=questions_path,
            shuffle_questions=False,
        ),
    )

    result = runner.invoke(app, ["--shuffle"])

    assert result.exit_code == 0
    assert called_with["path"] == questions_path
    assert called_with["shuffle_questions"] is True


def test_cli_without_shuffle_option_preserves_disabled_configuration(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Test that CLI preserves disabled shuffle configuration."""
    questions_path = tmp_path / "questions.json"
    questions_path.write_text("[]", encoding="utf-8")

    called_with: dict[str, object] = {}

    def fake_run_quiz(
        path: Path,
        *,
        category: str | None = None,
        shuffle_questions: bool = False,
    ) -> None:
        called_with["path"] = path
        called_with["shuffle_questions"] = shuffle_questions

    monkeypatch.setattr("puzzlebox.cli.run_quiz", fake_run_quiz)
    monkeypatch.setattr(
        "puzzlebox.cli.load_config",
        lambda _: AppConfig(
            questions_path=questions_path,
            shuffle_questions=False,
        ),
    )

    result = runner.invoke(app, [])

    assert result.exit_code == 0
    assert called_with["path"] == questions_path
    assert called_with["shuffle_questions"] is False


def test_create_runner_passes_category_to_create_quiz(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Test that create_runner passes category to quiz creation."""
    questions_path = tmp_path / "questions.json"
    questions_path.write_text(
        """
{
    "questions": [
        {
            "text": "Question 1",
            "answers": ["A", "B"],
            "correct_answer": "A",
            "category": "Math",
            "difficulty": "easy"
        }
    ]
}
""".strip(),
        encoding="utf-8",
    )

    called_with: dict[str, object] = {}

    def fake_create_quiz(
        repository,
        *,
        category: str | None = None,
        shuffle: bool = False,
    ) -> Quiz:
        called_with["repository"] = repository
        called_with["category"] = category
        called_with["shuffle"] = shuffle

        return Quiz(
            questions=(
                Question(
                    text="Test question",
                    answers=("A", "B"),
                    correct_answer="A",
                    category="Math",
                    difficulty=Difficulty.EASY,
                ),
            ),
        )

    monkeypatch.setattr(
        "puzzlebox.cli.create_quiz",
        fake_create_quiz,
    )

    create_runner(
        questions_path,
        category="Math",
    )

    assert called_with["category"] == "Math"


def test_run_quiz_passes_category_to_create_runner(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Test that run_quiz passes category to runner creation."""
    called_with: dict[str, object] = {}

    runner = Mock(spec=QuizRunner)
    runner.is_finished = False
    runner.score = 1
    runner.percentage = 100.0
    runner.current_question = Mock()
    runner.current_question.total = 1

    def fake_create_runner(
        questions_path: Path,
        *,
        category: str | None = None,
        shuffle_questions: bool = False,
    ) -> QuizRunner:
        called_with["questions_path"] = questions_path
        called_with["category"] = category
        called_with["shuffle_questions"] = shuffle_questions
        return runner

    def finish_quiz(_: QuizRunner) -> None:
        runner.is_finished = True

    monkeypatch.setattr(
        "puzzlebox.cli.create_runner",
        fake_create_runner,
    )
    monkeypatch.setattr(
        "puzzlebox.cli.process_question",
        finish_quiz,
    )

    run_quiz(
        tmp_path / "questions.json",
        category="Math",
    )

    assert called_with["category"] == "Math"


def test_cli_passes_configured_category_to_run_quiz(
    monkeypatch,
) -> None:
    """Test that the configured category is passed to run_quiz."""
    called_with: dict[str, object] = {}

    def fake_run_quiz(
        questions_path: Path,
        *,
        category: str | None = None,
        shuffle_questions: bool = False,
    ) -> None:
        called_with["questions_path"] = questions_path
        called_with["category"] = category
        called_with["shuffle_questions"] = shuffle_questions

    config = AppConfig(
        questions_path=Path("resources/questions.json"),
        shuffle_questions=False,
        category="Science",
    )

    monkeypatch.setattr(
        "puzzlebox.cli.load_config",
        lambda _: config,
    )
    monkeypatch.setattr(
        "puzzlebox.cli.run_quiz",
        fake_run_quiz,
    )

    result = runner.invoke(app, [])

    assert result.exit_code == 0
    assert called_with["category"] == "Science"
