#!/usr/bin/env python3
"""
Interactive PyPI Publishing Script
Handles TestPyPI and production PyPI uploads with validation.
"""

import argparse
import getpass
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional


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


def run_command(
    cmd: List[str], description: str, cwd: Optional[Path] = None
) -> subprocess.CompletedProcess:
    """Run a command with error handling and output."""
    print_status(f"Running: {' '.join(cmd[:3])}{'...' if len(cmd) > 3 else ''}", "info")
    try:
        result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
        if result.stdout.strip():
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print_status(f"Failed: {description}", "error")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        raise


def check_built_files(project_root: Path) -> Dict[str, List[Path]]:
    """Check for built distribution files."""
    print_status("Checking for built distribution files...", "info")

    dist_dir = project_root / "dist"
    if not dist_dir.exists():
        raise RuntimeError("No dist/ directory found. Please run: python scripts/build.py")

    wheel_files = list(dist_dir.glob("*.whl"))
    sdist_files = list(dist_dir.glob("*.tar.gz"))
    all_files = wheel_files + sdist_files

    if not all_files:
        raise RuntimeError(
            "No distribution files found in dist/. Please run: python scripts/build.py"
        )

    print_status(f"Found {len(all_files)} distribution files:", "success")
    for file in all_files:
        size_mb = file.stat().st_size / (1024 * 1024)
        print_status(f"  {file.name} ({size_mb:.1f} MB)", "info")

    return {"wheel": wheel_files, "sdist": sdist_files, "all": all_files}


def get_user_confirmation(message: str) -> bool:
    """Get user confirmation for actions."""
    while True:
        response = input(f"{Colors.YELLOW}{message} (y/n): {Colors.END}").lower().strip()
        if response in ["y", "yes"]:
            return True
        elif response in ["n", "no"]:
            return False
        else:
            print("Please answer 'y' or 'n'")


def check_credentials(repository: str) -> bool:
    """Check if PyPI credentials are available in ~/.pypirc."""
    print_status(f"Checking {repository} credentials in ~/.pypirc...", "info")

    try:
        from pathlib import Path

        pypirc_path = Path.home() / ".pypirc"

        if not pypirc_path.exists():
            print_status("~/.pypirc file not found", "warning")
            return False

        # Check if the repository section exists in ~/.pypirc
        pypirc_content = pypirc_path.read_text()
        if f"[{repository}]" in pypirc_content:
            print_status(f"Found {repository} configuration in ~/.pypirc", "success")
            return True
        else:
            print_status(f"No {repository} section found in ~/.pypirc", "warning")
            return False

    except Exception as e:
        print_status(f"Error checking ~/.pypirc: {e}", "warning")
        return False


def upload_to_repository(project_root: Path, repository: str, files: List[Path]) -> bool:
    """Upload files to specified repository using ~/.pypirc configuration."""
    if repository not in ["testpypi", "pypi"]:
        raise ValueError(f"Unknown repository: {repository}")

    print_status(f"Uploading to {repository} using ~/.pypirc...", "info")

    # Prepare twine upload command using repository name (will use ~/.pypirc)
    cmd = [
        "uv",
        "run",
        "--with",
        "twine",
        "twine",
        "upload",
        "--repository",
        repository,
    ]

    # Add file paths
    for file in files:
        cmd.append(str(file))

    try:
        run_command(cmd, f"upload to {repository}", project_root)
        print_status(f"Successfully uploaded to {repository}", "success")
        return True
    except subprocess.CalledProcessError as e:
        if "already exists" in str(e.stderr):
            print_status(f"Package version already exists on {repository}", "warning")
            return False
        else:
            print_status(f"Upload to {repository} failed", "error")
            raise


def test_installation(package_name: str, repository: str, version: str) -> bool:
    """Test package installation from repository."""
    print_status(f"Testing installation from {repository}...", "info")

    # Wait a bit for package to be available
    if repository == "testpypi":
        print_status("Waiting 30 seconds for package to be available...", "info")
        time.sleep(30)
    else:
        print_status("Waiting 10 seconds for package to be available...", "info")
        time.sleep(10)

    try:
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as temp_dir:
            # Test installation in isolated environment
            install_cmd = ["uv", "run", "--isolated", "--with"]

            if repository == "testpypi":
                install_cmd.extend(
                    [
                        f"--index-url",
                        "https://test.pypi.org/simple/",
                        f"--extra-index-url",
                        "https://pypi.org/simple/",  # For dependencies
                        f"{package_name}=={version}",
                    ]
                )
            else:
                install_cmd.extend([f"{package_name}=={version}"])

            install_cmd.extend(
                [
                    "python",
                    "-c",
                    f"import {package_name.replace('-', '_')}; print('Installation test successful')",
                ]
            )

            run_command(install_cmd, f"test installation from {repository}", Path(temp_dir))
            print_status(f"Installation test from {repository} passed", "success")
            return True

    except subprocess.CalledProcessError as e:
        print_status(f"Installation test from {repository} failed", "error")
        print(f"Error: {e}")
        return False


def get_package_version(project_root: Path) -> str:
    """Get package version from pyproject.toml."""
    import tomllib

    with open(project_root / "pyproject.toml", "rb") as f:
        pyproject_data = tomllib.load(f)

    return pyproject_data["project"]["version"]


def main():
    """Main upload script entry point."""
    parser = argparse.ArgumentParser(description="Interactive PyPI publishing script")
    parser.add_argument("--test", action="store_true", help="Upload to TestPyPI")
    parser.add_argument("--prod", action="store_true", help="Upload to production PyPI")
    parser.add_argument("--skip-tests", action="store_true", help="Skip installation tests")
    parser.add_argument("--force", action="store_true", help="Skip confirmation prompts")

    args = parser.parse_args()

    if not (args.test or args.prod):
        print_status("Please specify --test or --prod", "error")
        sys.exit(1)

    if args.test and args.prod:
        print_status("Please specify only one of --test or --prod", "error")
        sys.exit(1)

    project_root = Path(__file__).parent.parent
    package_name = "huoshui-pdf-translator"

    print_status(f"Publishing project from: {project_root}", "info")

    try:
        # Check for built files
        print_status("\n=== CHECKING DISTRIBUTION FILES ===", "info")
        files_info = check_built_files(project_root)

        # Get package version
        version = get_package_version(project_root)
        print_status(f"Package version: {version}", "info")

        # Determine target repository
        repository = "testpypi" if args.test else "pypi"
        repository_name = "TestPyPI" if args.test else "PyPI"

        # Confirmation
        if not args.force:
            print_status(f"\n=== UPLOAD CONFIRMATION ===", "info")
            print_status(f"Repository: {repository_name}", "info")
            print_status(f"Package: {package_name} v{version}", "info")
            print_status(f"Files to upload: {len(files_info['all'])}", "info")

            if not get_user_confirmation(f"Proceed with upload to {repository_name}?"):
                print_status("Upload cancelled by user", "warning")
                sys.exit(0)

        # Upload process
        print_status(f"\n=== UPLOADING TO {repository_name.upper()} ===", "info")

        upload_success = upload_to_repository(project_root, repository, files_info["all"])

        if not upload_success:
            print_status("Upload failed or package already exists", "warning")
            if not args.force and not get_user_confirmation(
                "Continue with installation test anyway?"
            ):
                sys.exit(1)

        # Test installation
        if not args.skip_tests and upload_success:
            print_status(f"\n=== TESTING INSTALLATION FROM {repository_name.upper()} ===", "info")
            test_success = test_installation(package_name, repository, version)

            if not test_success:
                print_status("Installation test failed", "warning")

        # Success summary
        print_status(f"\n=== UPLOAD COMPLETE ===", "success")
        print_status(f"Package uploaded to {repository_name}", "success")

        if repository == "testpypi":
            print_status("\nNext steps:", "info")
            print_status("1. Test installation:", "info")
            print_status(
                f"   uv add --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ {package_name}",
                "info",
            )
            print_status("2. If tests pass, upload to production:", "info")
            print_status("   python scripts/upload.py --prod", "info")
        else:
            print_status("\nPackage is now available on PyPI:", "info")
            print_status(f"   uv add {package_name}", "info")
            print_status(f"   https://pypi.org/project/{package_name}/", "info")

    except KeyboardInterrupt:
        print_status("\nUpload cancelled by user", "warning")
        sys.exit(1)
    except Exception as e:
        print_status(f"Upload failed with error: {e}", "error")
        sys.exit(1)


if __name__ == "__main__":
    main()
