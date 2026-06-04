import os

# Настройки
OUTPUT_FILE = "project_context.txt"
# Папки, которые точно НЕ нужны (добавь свои, если есть)
IGNORE_DIRS = {
    ".git",
    ".idea",
    "__pycache__",
    ".venv",
    "env",
    ".pytest_cache",
    "logs",
    # "tests",
}
# Расширения файлов, которые берем
INCLUDE_EXTS = {
    ".py",
    ".sql",
    ".html",
    ".css",
    ".js",
    ".md",
    ".txt",
    ".env.example",
    ".yml",
    "Dockerfile",
    ".sh",
}


def collect_code():
    project_root = os.getcwd()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        # Пишем дерево проекта в начало файла для понимания структуры
        outfile.write("=== PROJECT STRUCTURE ===\n")
        for root, dirs, files in os.walk(project_root):
            # Фильтрация папок
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            level = root.replace(project_root, "").count(os.sep)
            indent = " " * 4 * (level)
            outfile.write(f"{indent}{os.path.basename(root)}/\n")
            subindent = " " * 4 * (level + 1)
            for f in files:
                if any(f.endswith(ext) for ext in INCLUDE_EXTS) and f != OUTPUT_FILE:
                    outfile.write(f"{subindent}{f}\n")

        outfile.write("\n\n=== FILE CONTENTS ===\n\n")

        # Сбор содержимого
        for root, dirs, files in os.walk(project_root):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            for filename in files:
                # Пропускаем сам файл вывода и скрипт
                if filename in [OUTPUT_FILE, "context_maker.py"]:
                    continue

                # Проверяем расширение
                if not any(filename.endswith(ext) for ext in INCLUDE_EXTS):
                    continue

                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, project_root)

                outfile.write(f"\n{'=' * 50}\n")
                outfile.write(f"FILE: {rel_path}\n")
                outfile.write(f"{'=' * 50}\n")

                try:
                    with open(filepath, "r", encoding="utf-8") as infile:
                        outfile.write(infile.read())
                except Exception as e:
                    outfile.write(f"[Error reading file: {e}]")
                outfile.write("\n")

    print(f"Готово! Весь проект собран в {OUTPUT_FILE}")
    print(f"Размер файла: {os.path.getsize(OUTPUT_FILE) / 1024:.2f} KB")


if __name__ == "__main__":
    collect_code()
