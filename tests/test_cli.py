"""Tests for the command-line interface."""

from pathlib import Path

from puzzlebox.cli import run_quiz


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
