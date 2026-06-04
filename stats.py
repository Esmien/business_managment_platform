from pathlib import Path

IGNORE_DIRS = {
    ".venv",
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "migrations",
    "infra",
    "tests"
}

total_lines = 0

for file in Path(".").rglob("*.py"):
    if not set(file.parts) & IGNORE_DIRS:
        total_lines += sum(1 for line in open(file, 'r', encoding="utf-8", errors="ignore"))

print(f"Всего строк Python-кода: {total_lines}")