# PuzzleBox

[![Python](https://img.shields.io/badge/Python-3.13%2B-3776AB?logo=python\&logoColor=white)](https://www.python.org/)
[![uv](https://img.shields.io/badge/uv-package%20manager-DE5FE9?logo=uv\&logoColor=white)](https://docs.astral.sh/uv/)
[![Pytest](https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest\&logoColor=white)](https://docs.pytest.org/)
[![Coverage](https://img.shields.io/badge/coverage-90%25%2B-brightgreen?logo=pytest\&logoColor=white)](https://pytest-cov.readthedocs.io/)
[![Ruff](https://img.shields.io/badge/code%20quality-Ruff-D7FF64?logo=ruff\&logoColor=black)](https://docs.astral.sh/ruff/)
[![MyPy](https://img.shields.io/badge/type%20checking-MyPy-2F74C0?logo=python\&logoColor=white)](https://mypy.readthedocs.io/)

**Version: 1.0.0**

PuzzleBox is a small Python quiz application built as a learning and portfolio project.

The project focuses on clean Python code, domain modelling, validation, automated testing, error handling, configuration, and a clear separation between application logic and presentation.

## Features

* Multiple-choice quiz
* Questions loaded from JSON
* Pydantic-based input validation
* Domain models implemented with Python dataclasses
* Difficulty levels: easy, medium, hard
* Filtering questions by category
* Filtering questions by difficulty
* Optional question shuffling
* Repository abstraction for question loading
* Quiz session and scoring logic
* Interactive command-line interface
* YAML-based application configuration
* Command-line options for overriding configuration
* Structured application logging
* Custom error handling for invalid question data
* Automated tests with pytest
* Test coverage enforcement
* Static type checking with MyPy
* Code quality and formatting with Ruff

## Tech Stack

| Technology   | Purpose                           |
| ------------ | --------------------------------- |
| Python 3.13+ | Application language              |
| uv           | Dependency and project management |
| Typer        | Command-line interface            |
| Pydantic v2  | Data validation                   |
| PyYAML       | YAML configuration                |
| pytest       | Automated testing                 |
| pytest-cov   | Test coverage                     |
| Ruff         | Linting and formatting            |
| MyPy         | Static type checking              |

## Project Structure

```text
puzzlebox/
├── config/
│   └── settings.yaml
├── resources/
│   └── questions.json
├── scripts/
│   └── quality.py
├── src/
│   └── puzzlebox/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── logging.py
│       ├── main.py
│       ├── models.py
│       ├── presentation.py
│       ├── questions.py
│       ├── quiz.py
│       ├── repositories.py
│       └── runner.py
├── tests/
│   ├── ...
├── .gitignore
├── pyproject.toml
├── README.md
└── uv.lock
```

## Installation

### Requirements

* Python 3.13 or newer
* [uv](https://docs.astral.sh/uv/)

Clone the repository and install the project dependencies:

```bash
git clone https://github.com/sendersk/puzzlebox.git
cd puzzlebox
uv sync
```

## Usage

### Start the quiz

The default configuration points to:

```text
resources/questions.json
```

Start PuzzleBox with:

```bash
uv run puzzlebox
```

### Command-line options

Display the available options with:

```bash
uv run puzzlebox --help
```

#### Custom question file

A different JSON file can be supplied using the `--questions` or `-q` option:

```bash
uv run puzzlebox --questions path/to/questions.json
```

or:

```bash
uv run puzzlebox -q path/to/questions.json
```

The command-line option takes precedence over the path configured in `config/settings.yaml`.

#### Shuffle questions

Questions can be shuffled before the quiz starts:

```bash
uv run puzzlebox --shuffle
```

#### Filter by difficulty

Questions can be filtered by difficulty:

```bash
uv run puzzlebox --difficulty easy
```

Available values are:

```text
easy
medium
hard
```

#### Combine filters

Category and difficulty filters can be configured together:

```bash
uv run puzzlebox --difficulty hard
```

Category filtering is currently configured through `config/settings.yaml`.

### Configuration

The application configuration is stored in:

```text
config/settings.yaml
```

Example:

```yaml
questions_path: resources/questions.json
shuffle_questions: false
category: null
difficulty: null
```

The configuration supports:

* `questions_path` — path to the JSON question file
* `shuffle_questions` — whether to shuffle questions
* `category` — optional question category filter
* `difficulty` — optional difficulty filter

Command-line options override the corresponding configuration values where supported.

## Question Format

Questions are stored in JSON.

Example:

```json
{
  "questions": [
    {
      "text": "What is the capital of Germany?",
      "answers": [
        "Berlin",
        "Munich",
        "Hamburg",
        "Frankfurt"
      ],
      "correct_answer": "Berlin",
      "category": "Geography",
      "difficulty": "easy"
    }
  ]
}
```

The input data is validated before it is converted into domain objects.

Invalid files or invalid question data result in a controlled `QuestionLoadingError` instead of exposing low-level implementation errors to the CLI user.

## Architecture

PuzzleBox uses a small layered structure designed to keep responsibilities separated without introducing unnecessary complexity.

```text
                    ┌──────────────┐
                    │     CLI      │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Quiz Runner  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Quiz /       │
                    │ Session      │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Domain     │
                    │    Models    │
                    └──────────────┘
                           ▲
                           │
                    ┌──────┴───────┐
                    │ Repository   │
                    │ abstraction  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ JSON Loader  │
                    └──────────────┘
```

### Main components

**Domain models**

`models.py` contains the core quiz concepts:

* `Question`
* `Quiz`
* `QuizSession`
* `Difficulty`

The domain models contain business rules such as question validation, scoring, and quiz session state.

**Question loading**

`questions.py` is responsible for:

* reading the JSON file,
* validating its structure,
* converting validated data into domain objects,
* translating low-level loading and validation errors into `QuestionLoadingError`.

**Repository**

`repositories.py` defines the question repository abstraction and provides the JSON implementation.

This keeps the quiz creation logic independent of the concrete storage mechanism.

**Quiz**

`quiz.py` creates a `Quiz` from a question repository and applies optional category, difficulty, and shuffle operations.

**Runner**

`runner.py` provides an interface between the quiz session and the presentation layer.

It also contains `QuestionView`, a presentation-oriented view model used to expose question data to the CLI.

**Presentation**

`presentation.py` contains CLI presentation helpers such as displaying questions, reading answers, and displaying quiz results.

**Configuration**

`config.py` loads and validates application configuration from YAML.

**Logging**

`logging.py` provides centralized application logging configuration.

## Testing

PuzzleBox uses `pytest` for automated testing.

Run the complete test suite with:

```bash
uv run pytest
```

Run tests with coverage:

```bash
uv run pytest --cov=src/puzzlebox --cov-report=term-missing
```

The project enforces a minimum test coverage of **90%**.

The current v1.0.0 test suite contains **134 tests** and achieves approximately **99.45% coverage**.

The test suite covers:

* domain model validation,
* quiz session behaviour,
* question loading,
* invalid input handling,
* repository behaviour,
* question filtering,
* question shuffling,
* configuration loading,
* CLI behaviour,
* command-line option precedence,
* presentation functions,
* logging,
* error handling.

## Quality Checks

All local quality checks can be executed with a single command:

```bash
uv run python scripts/quality.py
```

The script runs:

1. Ruff linting
2. Ruff formatting check
3. MyPy type checking
4. pytest with coverage

This provides a single local quality gate before committing changes.

Individual checks can also be run separately:

```bash
uv run ruff check .
```

```bash
uv run ruff format --check .
```

```bash
uv run mypy src
```

```bash
uv run pytest --cov=src/puzzlebox --cov-report=term-missing
```

## Development

PuzzleBox was developed incrementally, with a focus on small, testable changes.

The project follows several principles:

* Python 3.13+
* type hints throughout the codebase
* PEP 8-compatible formatting
* `pathlib` for filesystem operations
* Pydantic for external data validation
* dataclasses for domain objects where appropriate
* explicit error handling
* logging instead of using `print()` for application diagnostics
* automated testing with pytest
* static type checking with MyPy
* linting and formatting with Ruff
* small, focused modules with clear responsibilities
* avoiding unnecessary abstraction and overengineering

## Learning Goals

PuzzleBox was created as a practical Python learning project.

The project is used to practice:

* Python application structure
* object-oriented and data-oriented design
* dataclasses and enums
* type hints
* Pydantic validation
* exceptions and error handling
* file handling with `pathlib`
* JSON and YAML
* dependency injection
* protocols and abstractions
* CLI development
* logging
* automated testing
* test coverage
* linting and formatting
* static type checking
* Git-based incremental development

## Roadmap

The initial development goal was to complete a stable **v1.0.0** release with a clean, well-tested CLI application.

Version 1.0.0 provides the core quiz functionality, including:

* JSON-based question loading
* input validation
* quiz session management
* scoring
* category and difficulty filtering
* question shuffling
* YAML configuration
* CLI configuration overrides
* structured logging
* automated testing
* static type checking
* linting and formatting

Possible future improvements may be considered for later versions rather than being added to the initial release.

Examples include:

* graphical user interface
* additional quiz modes
* persistent results
* additional question sources
* improved user experience

## License

This project is currently intended as a personal learning and portfolio project.
