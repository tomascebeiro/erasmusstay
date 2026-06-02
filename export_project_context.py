#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import argparse

# Carpetas que no se exportan
IGNORED_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "htmlcov",
    "staticfiles",
    "media",
    "uploads",
    ".next",
    ".nuxt",
}

# Extensiones que no interesa meter en texto
IGNORED_EXTENSIONS = {
    ".pyc", ".pyo", ".pyd",
    ".sqlite3", ".db",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".svg",
    ".pdf", ".zip", ".rar", ".7z", ".tar", ".gz",
    ".mp4", ".mov", ".avi", ".mp3", ".wav",
    ".woff", ".woff2", ".ttf", ".otf",
    ".lock",
}

# Archivos concretos que sí suelen aportar contexto
IMPORTANT_FILENAMES = {
    "manage.py",
    "requirements.txt",
    "requirements-dev.txt",
    "pyproject.toml",
    "Pipfile",
    "Pipfile.lock",
    "poetry.lock",
    ".env.example",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "package.json",
    "vite.config.js",
    "vite.config.ts",
    "vue.config.js",
    "tsconfig.json",
    "jsconfig.json",
    "tailwind.config.js",
    "tailwind.config.ts",
    "postcss.config.js",
    "README.md",
}

# Patrones típicos relevantes en Django/Vue
IMPORTANT_SUFFIXES = (
    "settings.py",
    "urls.py",
    "models.py",
    "views.py",
    "serializers.py",
    "forms.py",
    "admin.py",
    "apps.py",
    "permissions.py",
    "filters.py",
    "tests.py",
    "test_models.py",
    "test_views.py",
    "test_api.py",
    "router.js",
    "router.ts",
    "store.js",
    "store.ts",
    "main.js",
    "main.ts",
    "App.vue",
)

IMPORTANT_EXTENSIONS = {
    ".py",
    ".vue",
    ".js",
    ".ts",
    ".css",
    ".scss",
    ".html",
    ".json",
    ".md",
    ".yml",
    ".yaml",
    ".toml",
}

DEFAULT_MAX_FILE_SIZE_KB = 140


def is_ignored_path(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def should_include_file(path: Path, max_file_size_kb: int) -> bool:
    if is_ignored_path(path):
        return False

    if path.suffix.lower() in IGNORED_EXTENSIONS:
        return False

    if path.name in IMPORTANT_FILENAMES:
        return True

    if path.name.endswith(IMPORTANT_SUFFIXES):
        return True

    if path.suffix.lower() in IMPORTANT_EXTENSIONS:
        try:
            return path.stat().st_size <= max_file_size_kb * 1024
        except OSError:
            return False

    return False


def safe_read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
        except OSError as exc:
            return f"[ERROR LENDO ARQUIVO: {exc}]"

    return "[ARQUIVO NON TEXTO OU CODIFICACIÓN NON SOPORTADA]"


def build_tree(root: Path, max_depth: int = 5) -> str:
    lines = []

    def walk(directory: Path, prefix: str = "", depth: int = 0):
        if depth > max_depth:
            return

        try:
            entries = sorted(
                [p for p in directory.iterdir() if not is_ignored_path(p.relative_to(root))],
                key=lambda p: (p.is_file(), p.name.lower())
            )
        except OSError:
            return

        for index, entry in enumerate(entries):
            connector = "└── " if index == len(entries) - 1 else "├── "
            rel = entry.relative_to(root)
            lines.append(f"{prefix}{connector}{entry.name}")

            if entry.is_dir():
                extension = "    " if index == len(entries) - 1 else "│   "
                walk(entry, prefix + extension, depth + 1)

    lines.append(root.name + "/")
    walk(root)
    return "\n".join(lines)


def collect_files(root: Path, max_file_size_kb: int) -> list[Path]:
    files = []

    for path in root.rglob("*"):
        if path.is_file() and should_include_file(path.relative_to(root), max_file_size_kb):
            files.append(path)

    return sorted(files, key=lambda p: str(p.relative_to(root)).lower())


def write_export(root: Path, output: Path, max_file_size_kb: int, max_depth: int):
    files = collect_files(root, max_file_size_kb)

    with output.open("w", encoding="utf-8") as out:
        out.write("# CONTEXTO DO PROXECTO DJANGO + VUE\n\n")
        out.write(f"Xerado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        out.write(f"Raíz: {root.resolve()}\n")
        out.write(f"Arquivos incluídos: {len(files)}\n")
        out.write(f"Tamaño máximo por arquivo: {max_file_size_kb} KB\n\n")

        out.write("=" * 90 + "\n")
        out.write("ESTRUTURA DO PROXECTO\n")
        out.write("=" * 90 + "\n\n")
        out.write(build_tree(root, max_depth=max_depth))
        out.write("\n\n")

        out.write("=" * 90 + "\n")
        out.write("ARQUIVOS\n")
        out.write("=" * 90 + "\n\n")

        for file_path in files:
            rel = file_path.relative_to(root)
            size_kb = file_path.stat().st_size / 1024

            out.write("\n" + "=" * 90 + "\n")
            out.write(f"ARQUIVO: {rel}\n")
            out.write(f"TAMAÑO: {size_kb:.1f} KB\n")
            out.write("=" * 90 + "\n\n")

            content = safe_read_text(file_path)

            out.write(f"```{file_path.suffix.lstrip('.') or 'txt'}\n")
            out.write(content)
            if not content.endswith("\n"):
                out.write("\n")
            out.write("```\n")

    print(f"Exportación creada: {output}")
    print(f"Arquivos incluídos: {len(files)}")


def main():
    parser = argparse.ArgumentParser(
        description="Exporta contexto dun proxecto Django + Vue a un único TXT."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Raíz do proxecto. Por defecto: directorio actual."
    )
    parser.add_argument(
        "--output",
        default="project_context_django_vue.txt",
        help="Arquivo de saída."
    )
    parser.add_argument(
        "--max-file-size-kb",
        type=int,
        default=DEFAULT_MAX_FILE_SIZE_KB,
        help="Tamaño máximo por arquivo en KB."
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=5,
        help="Profundidade máxima da árbore de carpetas."
    )

    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = Path(args.output).resolve()

    if not root.exists():
        raise SystemExit(f"A raíz indicada non existe: {root}")

    write_export(
        root=root,
        output=output,
        max_file_size_kb=args.max_file_size_kb,
        max_depth=args.max_depth,
    )


if __name__ == "__main__":
    main()