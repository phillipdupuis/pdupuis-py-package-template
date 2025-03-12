#!/usr/bin/env python3

"""Initialize a Python package template by replacing placeholders in files and filenames."""

import argparse
import os
import shutil
import subprocess
import tempfile
from contextlib import ContextDecorator
from pathlib import Path
from typing import Any, TypedDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent

REWRITE_FILES = [
    ".github/workflows/lint.yml",
    ".github/workflows/publish.yml",
    ".github/dependabot.yml",
    "src/${project_name}/__init__.py",
    "tests/__init__.py",
    "pyproject.toml",
    "README.md",
]

RENAME_PATHS = ["src/${project_name}"]


Replacements = TypedDict(
    "Replacements",
    {
        r"${project_name}": str,
        r"${author}": str,
        r"${email}": str,
        r"${description}": str,
        r"${github_username}": str,
    },
)


class cwd(ContextDecorator):
    """Context manager for temporarily changing the current working directory."""

    def __init__(self, path: Path):
        self.path = path.resolve()

    def __enter__(self):
        self.old_cwd = Path.cwd()
        os.chdir(self.path)

    def __exit__(self, *exc: Any):
        os.chdir(self.old_cwd)


@cwd(PROJECT_ROOT)
def main(replacements: Replacements) -> None:
    """Main function to initialize the library template."""

    print("Initializing template with replacements:")
    for key, value in replacements.items():
        print(f"  {key} -> {value}")

    print("Replacing placeholders in files...")
    for file in REWRITE_FILES:
        rewrite_file(Path(file), replacements)

    print("Updating path names...")
    for path in RENAME_PATHS:
        rename_path(Path(path), replacements)

    set_codecov_token_secret_in_github()

    print(f"'{replacements['${project_name}']}' is ready to use.")


def parse_args() -> Replacements:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Replace placeholders in a Python library template"
    )
    parser.add_argument("-n", "--name", required=True, help="Library name (snake_case recommended)")
    parser.add_argument(
        "-a",
        "--author",
        required=True,
        help="Author name",
    )
    parser.add_argument(
        "-e",
        "--email",
        required=True,
        help="Author email",
    )
    parser.add_argument(
        "-g",
        "--github",
        required=True,
        help="GitHub username",
    )
    parser.add_argument(
        "-d",
        "--description",
        default="A Python package",
        help="Short package description",
    )
    args = parser.parse_args()
    return {
        "${project_name}": args.name,
        "${author}": args.author,
        "${email}": args.email,
        "${description}": args.description,
        "${github_username}": args.github,
    }


def confirm(message: str) -> bool:
    """Ask the user for confirmation before proceeding."""
    response = input(f"{message}\n[y/n]: ")
    return response.lower() == "y"


def rewrite_file(path: Path, replacements: Replacements) -> None:
    """Replace all placeholders in a file text contents."""
    try:
        text = path.read_text(encoding="utf-8")
        placeholders = [k for k in replacements.keys() if k in text]
        if not placeholders:
            print(f"No placeholders found in file: {path}")
            return

        for placeholder in placeholders:
            value = replacements[placeholder]  # type: ignore
            assert isinstance(value, str)
            text = text.replace(placeholder, value)

        path.write_text(text, encoding="utf-8")
        print(f"Updated {path}")

    except UnicodeDecodeError:
        print(f"  Skipping binary file: {path}")

    except Exception as e:
        print(f"  Error processing {path}: {e}")


def rename_path(path: Path, replacements: Replacements) -> None:
    """Replace all placeholders in a file or directory name."""
    placeholders = [k for k in replacements.keys() if k in path.name]
    if not placeholders:
        print(f"No placeholders found in path: {path}")
        return

    new_path = path.with_name(path.name)
    for placeholder in placeholders:
        value = replacements[placeholder]  # type: ignore
        assert isinstance(value, str)
        new_path = new_path.with_name(new_path.name.replace(placeholder, value))

    shutil.move(path, new_path)
    print(f"Renamed: {path} -> {new_path}")


def set_codecov_token_secret_in_github():
    """Attempt to set the CODECOV_TOKEN secret for use in GitHub Actions."""
    token = os.environ.get("CODECOV_TOKEN")

    if not token:
        print("No CODECOV_TOKEN environment variable found.")
        return

    if not confirm(
        "It appears a CODECOV_TOKEN environment variable is defined.\n"
        "Would you like to set it as the CODECOV_TOKEN secret in GitHub Actions?"
    ):
        return

    with tempfile.NamedTemporaryFile(mode="w+t", delete=False) as token_file:
        token_file.write(token)
    try:
        subprocess.run(["gh", "secret", "set", "CODECOV_TOKEN", "<", token_file.name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to set CODECOV_TOKEN secret: {e}")
    finally:
        os.unlink(token_file.name)


if __name__ == "__main__":
    main(parse_args())
