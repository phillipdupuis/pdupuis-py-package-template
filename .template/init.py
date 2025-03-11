#!/usr/bin/env python3

"""Initialize a Python package template by replacing placeholders in files and filenames."""

import argparse
import fnmatch
import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()


@dataclass
class Args:
    name: str
    author: str
    email: str
    description: str
    github: str


def get_git_config(key: str, default: str | None = None):
    """Get a git config value, or return the default if not found."""
    try:
        return (
            subprocess.check_output(["git", "config", "--get", key], text=True).strip() or default
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return default


def get_gitignore_patterns() -> list[str]:
    """Parse the .gitignore file and return a list of patterns."""
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        lines = [line.strip() for line in gitignore_path.read_text().splitlines()]
        return [line for line in lines if line and not line.startswith("#")]
    return []


def is_ignored(path: Path, gitignore_patterns: list[str]) -> bool:
    """Check if a path should be ignored based on gitignore patterns."""
    path = path.resolve().relative_to(PROJECT_ROOT)

    if ".git" in path.parts or ".github" in path.parts:
        return True

    path_str = str(path.relative_to(Path.cwd()))

    for pattern in gitignore_patterns:
        # Handle directory patterns (ending with /)
        if pattern.endswith("/"):
            if path.is_dir() and fnmatch.fnmatch(path_str + "/", pattern + "*"):
                return True
        # Use fnmatch for glob pattern matching
        elif fnmatch.fnmatch(path_str, pattern):
            return True

    return False


def parse_args() -> Args:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Replace placeholders in a Python package template"
    )
    parser.add_argument("-n", "--name", required=True, help="Package name (snake_case recommended)")
    parser.add_argument(
        "-a", "--author", default=get_git_config("user.name", "Your Name"), help="Author name"
    )
    parser.add_argument(
        "-e",
        "--email",
        default=get_git_config("user.email", "your.email@example.com"),
        help="Author email",
    )
    parser.add_argument(
        "-d",
        "--description",
        default="A Python package",
        help="Short package description",
    )
    parser.add_argument(
        "-g",
        "--github",
        default=None,
        help="GitHub username",
    )

    args = parser.parse_args()

    # If GitHub username is not provided, try to derive it from email or use system username
    if args.github is None:
        if "@" in args.email:
            args.github = args.email.split("@")[0]
        else:
            import getpass

            args.github = getpass.getuser()

    return Args(
        name=args.name,
        author=args.author,
        email=args.email,
        description=args.description,
        github=args.github,
    )


def confirm_replacements(replacements: dict[str, str]) -> None:
    """Display the planned replacements and ask for confirmation."""
    print("Initializing template with:")
    for key, value in replacements.items():
        print(f"  {key}: {value}")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    input()


def replace_in_file(path: Path, replacements: dict[str, str]) -> None:
    """Replace all placeholders in a file."""
    try:
        text = path.read_text(encoding="utf-8")
        for key, value in replacements.items():
            text = text.replace(key, value)
        path.write_text(text, encoding="utf-8")
        print(f"Updated {path}")
    except UnicodeDecodeError:
        print(f"  Skipping binary file: {path}")
    except Exception as e:
        print(f"  Error processing {path}: {e}")


def rename_files_and_dirs(directory: Path, replacements: dict[str, str]) -> None:
    """Rename files and directories with placeholders in their names."""
    # Process all files (including hidden ones)
    for root, dirs, files in os.walk(directory, topdown=False):
        # Process files first
        for file in files:
            file_path = os.path.join(root, file)
            if "${" in file:
                new_name = file
                for placeholder, value in replacements.items():
                    new_name = new_name.replace(placeholder, value)

                new_path = os.path.join(root, new_name)
                if file_path != new_path:
                    print(f"Renaming: {file_path} -> {new_path}")
                    os.makedirs(os.path.dirname(new_path), exist_ok=True)
                    shutil.move(file_path, new_path)

        # Then process directories (bottom-up)
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if "${" in dir_name:
                new_name = dir_name
                for placeholder, value in replacements.items():
                    new_name = new_name.replace(placeholder, value)

                new_path = os.path.join(root, new_name)
                if dir_path != new_path:
                    print(f"Renaming directory: {dir_path} -> {new_path}")
                    if not os.path.exists(new_path):
                        os.makedirs(os.path.dirname(new_path), exist_ok=True)
                        shutil.move(dir_path, new_path)


def main():
    """Main function to initialize the template."""
    args = parse_args()

    # Generate derived replacements
    import_name = args.name.replace("-", "_")
    package_title = import_name  # Keep it simple
    current_year = str(datetime.now().year)

    # Create replacements dictionary and confirm them
    replacements = {
        r"${package_name}": args.name,
        r"${import_name}": import_name,
        r"${package_title}": package_title,
        r"${author}": args.author,
        r"${email}": args.email,
        r"${description}": args.description,
        r"${github_username}": args.github,
        r"${year}": current_year,
    }
    confirm_replacements(replacements)

    # Step 1: Replace placeholders in file contents
    print("Step 1: Replacing placeholders in file contents...")
    script_path = Path(__file__).resolve()

    for file_path in Path(".").rglob("*"):
        file_path = file_path.resolve()
        if (
            file_path.is_file()
            and ".git" not in file_path.parts
            and ".github" not in file_path.parts
            and file_path != script_path
        ):
            replace_in_file(file_path, replacements)

    # Step 2: Rename files and directories with placeholders
    print("Step 2: Renaming files and directories with placeholders...")
    rename_files_and_dirs(Path(".").resolve(), replacements)

    # Step 3: Remove this script if it's in the template repo
    if script_path.exists():
        print("Step 3: Removing initialization script...")
        os.remove(script_path)

    # Step 4: Create initial git repository if needed
    if not os.path.exists(".git"):
        print("Step 4: Creating initial git repository...")
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit from template"], check=True)

    print("Template initialization complete!")
    print(f"Your Python package '{args.name}' is ready to use.")


if __name__ == "__main__":
    main()
