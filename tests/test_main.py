from puzzlebox.main import main


def test_main(monkeypatch) -> None:
    """Test that the application entry point starts the CLI."""
    called = False

    def fake_app() -> None:
        nonlocal called
        called = True

    monkeypatch.setattr("puzzlebox.main.app", fake_app)

    main()

    assert called
