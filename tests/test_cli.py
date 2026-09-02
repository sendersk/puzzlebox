"""Tests for the command-line interface."""

from pathlib import Path

from typer.testing import CliRunner

from puzzlebox.cli import app, run_quiz
from puzzlebox.config import AppConfig

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

    called_with: dict[str, Path] = {}

    def fake_run_quiz(path: Path) -> None:
        called_with["path"] = path

    monkeypatch.setattr("puzzlebox.cli.run_quiz", fake_run_quiz)

    result = runner.invoke(
        app,
        ["--questions", str(questions_path)],
    )

    assert result.exit_code == 0
    assert called_with["path"] == questions_path


def test_cli_accepts_short_questions_option(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Test that the CLI accepts the short questions option."""
    questions_path = tmp_path / "questions.json"
    questions_path.write_text("[]", encoding="utf-8")

    called_with: dict[str, Path] = {}

    def fake_run_quiz(path: Path) -> None:
        called_with["path"] = path

    monkeypatch.setattr("puzzlebox.cli.run_quiz", fake_run_quiz)

    result = runner.invoke(
        app,
        ["-q", str(questions_path)],
    )

    assert result.exit_code == 0
    assert called_with["path"] == questions_path


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

    called_with: dict[str, Path] = {}

    def fake_run_quiz(path: Path) -> None:
        called_with["path"] = path

    monkeypatch.setattr("puzzlebox.cli.run_quiz", fake_run_quiz)
    monkeypatch.setattr(
        "puzzlebox.cli.load_config",
        lambda _: AppConfig(questions_path=questions_path),
    )

    result = runner.invoke(app, [])

    assert result.exit_code == 0
    assert called_with["path"] == questions_path


def test_cli_option_overrides_config(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Test that the CLI option overrides the configured questions path."""
    configured_path = tmp_path / "configured.json"
    cli_path = tmp_path / "cli.json"

    configured_path.write_text("[]", encoding="utf-8")
    cli_path.write_text("[]", encoding="utf-8")

    called_with: dict[str, Path] = {}

    def fake_run_quiz(path: Path) -> None:
        called_with["path"] = path

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
