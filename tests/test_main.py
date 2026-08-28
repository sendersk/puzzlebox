"""Tests for PuzzleBox application entry point."""

from puzzlebox.main import main


def test_main(capsys) -> None:
    """Test that the application entry point produces the expected output."""
    main()

    captured = capsys.readouterr()

    assert captured.out == "PuzzleBox\n"
