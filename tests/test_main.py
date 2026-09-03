from puzzlebox.main import main


def test_main_configures_logging_before_starting_cli(
    monkeypatch,
) -> None:
    """Test that logging is configured before the CLI starts."""
    calls: list[str] = []

    def fake_configure_logging() -> None:
        calls.append("logging")

    def fake_app() -> None:
        calls.append("app")

    monkeypatch.setattr(
        "puzzlebox.main.configure_logging",
        fake_configure_logging,
    )
    monkeypatch.setattr(
        "puzzlebox.main.app",
        fake_app,
    )

    main()

    assert calls == ["logging", "app"]
