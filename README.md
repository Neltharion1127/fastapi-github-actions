# FastAPI GitHub Actions CI Demo

A minimal FastAPI service with **production-style Continuous Integration (CI)** using **GitHub Actions**.

This repository demonstrates how to enforce **code quality and correctness** through automated linting and testing across **multiple Python versions**.

---

## ✨ Features

- FastAPI web service
- Automated testing with `pytest`
- Static code analysis with `ruff`
- Dependency management via `uv` + `uv.lock`
- GitHub Actions CI pipeline
- Matrix testing on **Python 3.11 / 3.12 / 3.13**
- Main branch protected by CI checks

---

##  Project Structure

```text
.
├── app/
│   ├── __init__.py
│   └── main.py          # FastAPI application
├── tests/
│   └── test_api.py      # API tests
├── .github/
│   └── workflows/
│       └── ci.yaml      # GitHub Actions CI pipeline
├── pyproject.toml
├── uv.lock
└── README.md
```

---

##  API Endpoints

| Method | Path       | Description                   |
|--------|------------|-------------------------------|
| GET    | `/health`  | Health check                  |
| GET    | `/hello`   | Greeting endpoint             |
| GET    | `/metrics` | In-process metrics (mock)     |

---

## Running Locally

### 1. Install dependencies

```bash
pip install uv
uv sync
```

### 2. Run tests

```bash
uv run pytest -q
```

### 3. Run lint

```bash
uv run ruff check .
```

### 4. Start the server

```bash
uv run uvicorn app.main:app --reload
```

---

## Continuous Integration (CI)

This project uses **GitHub Actions** to automatically run checks on every push and pull request.

### CI Pipeline Steps

1. Checkout source code
2. Set up Python environment
3. Install dependencies via `uv`
4. Run `ruff` for static analysis
5. Run `pytest` for test verification

### Python Version Matrix

The CI pipeline validates the project against the following Python versions:

- Python 3.11
- Python 3.12
- Python 3.13

This ensures compatibility across multiple Python runtimes.

---

## Why This Project Exists

This repository is intentionally minimal.

It serves primarily as a **template/demo repository** showcasing a clean and repeatable CI setup with GitHub Actions, rather than a feature-complete application.

Its purpose is to demonstrate:

- Clean project structure
- Reliable dependency locking
- Automated quality gates
- Modern CI practices with GitHub Actions

It is designed as a **CI template** that can be reused for larger FastAPI or backend projects.

---

## License

MIT