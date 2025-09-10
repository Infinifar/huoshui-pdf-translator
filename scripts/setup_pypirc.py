#!/usr/bin/env python3
"""
Setup ~/.pypirc configuration for PyPI publishing
Interactive script to help users configure their PyPI credentials.
"""

import getpass
import sys
from pathlib import Path


# Color codes for output
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_status(message: str, status: str = "info") -> None:
    """Print colored status messages."""
    color = {
        "success": Colors.GREEN,
        "warning": Colors.YELLOW,
        "error": Colors.RED,
        "info": Colors.BLUE,
    }.get(status, Colors.BLUE)

    print(f"{color}{Colors.BOLD}[{status.upper()}]{Colors.END} {message}")


def get_user_input(prompt: str, required: bool = True) -> str:
    """Get user input with validation."""
    while True:
        response = input(f"{Colors.BLUE}{prompt}: {Colors.END}").strip()
        if response or not required:
            return response
        print_status("This field is required. Please enter a value.", "warning")


def get_user_confirmation(message: str) -> bool:
    """Get user confirmation."""
    while True:
        response = input(f"{Colors.YELLOW}{message} (y/n): {Colors.END}").lower().strip()
        if response in ["y", "yes"]:
            return True
        elif response in ["n", "no"]:
            return False
        else:
            print("Please answer 'y' or 'n'")


def main():
    """Main setup script."""
    print_status("PyPI Configuration Setup", "info")
    print()
    print("This script will help you set up ~/.pypirc for automated PyPI publishing.")
    print("You'll need your PyPI API tokens from:")
    print("• Production PyPI: https://pypi.org/manage/account/token/")
    print("• TestPyPI: https://test.pypi.org/manage/account/token/")
    print()

    pypirc_path = Path.home() / ".pypirc"

    # Check if ~/.pypirc already exists
    if pypirc_path.exists():
        print_status(f"Found existing ~/.pypirc file", "warning")
        if not get_user_confirmation("Do you want to overwrite it?"):
            print_status("Setup cancelled", "info")
            sys.exit(0)

        # Backup existing file
        backup_path = pypirc_path.with_suffix(".pypirc.backup")
        pypirc_path.rename(backup_path)
        print_status(f"Backed up existing file to {backup_path}", "info")

    print()
    print_status("Setting up PyPI credentials...", "info")
    print()

    # Get production PyPI token
    print("🔐 Production PyPI (pypi.org)")
    prod_token = getpass.getpass("Enter your production PyPI API token (pypi-...): ")
    if not prod_token.startswith("pypi-"):
        print_status("Warning: PyPI tokens usually start with 'pypi-'", "warning")

    print()
    # Get TestPyPI token
    print("🧪 TestPyPI (test.pypi.org)")
    test_needed = get_user_confirmation(
        "Do you want to configure TestPyPI? (recommended for testing)"
    )
    test_token = ""
    if test_needed:
        test_token = getpass.getpass("Enter your TestPyPI API token (pypi-...): ")
        if not test_token.startswith("pypi-"):
            print_status("Warning: TestPyPI tokens usually start with 'pypi-'", "warning")

    # Create ~/.pypirc content
    pypirc_content = "[distutils]\n"
    if test_needed:
        pypirc_content += "index-servers =\n    pypi\n    testpypi\n\n"
    else:
        pypirc_content += "index-servers =\n    pypi\n\n"

    pypirc_content += "[pypi]\n"
    pypirc_content += "repository = https://upload.pypi.org/legacy/\n"
    pypirc_content += "username = __token__\n"
    pypirc_content += f"password = {prod_token}\n"

    if test_needed and test_token:
        pypirc_content += "\n[testpypi]\n"
        pypirc_content += "repository = https://test.pypi.org/legacy/\n"
        pypirc_content += "username = __token__\n"
        pypirc_content += f"password = {test_token}\n"

    # Write the file
    try:
        pypirc_path.write_text(pypirc_content)

        # Set secure permissions (readable only by owner)
        pypirc_path.chmod(0o600)

        print()
        print_status("✅ ~/.pypirc configuration created successfully!", "success")
        print_status(f"File location: {pypirc_path}", "info")
        print_status("File permissions set to 600 (owner read/write only)", "info")

        print()
        print_status("Next steps:", "info")
        print("• Test your configuration:")
        print("  python scripts/upload.py --test")
        print("• For production publishing:")
        print("  python scripts/upload.py --prod")
        print("• Or use make commands:")
        print("  make test-upload")
        print("  make prod-upload")

    except Exception as e:
        print_status(f"Error creating ~/.pypirc: {e}", "error")
        sys.exit(1)


if __name__ == "__main__":
    main()
