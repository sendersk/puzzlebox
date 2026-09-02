from pathlib import Path

from puzzlebox.main import main


def test_main(monkeypatch) -> None:
    """Test that the application entry point starts the quiz."""
    called_with: dict[str, Path] = {}

    def fake_run_quiz(questions_path: Path) -> None:
        called_with["path"] = questions_path

    monkeypatch.setattr("puzzlebox.main.run_quiz", fake_run_quiz)

    main()

    assert called_with["path"] == Path("resources/questions.json")
