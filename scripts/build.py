#!/usr/bin/env python3
"""
Automated PyPI Build Script with Validation
Handles the complete build process with quality checks and validation.
"""

import argparse
import shutil
import subprocess
import sys
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
    print_status(f"Running: {' '.join(cmd)}", "info")
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


def check_project_structure(project_root: Path) -> Dict[str, bool]:
    """Validate project structure and required files."""
    print_status("Checking project structure...", "info")

    checks = {
        "pyproject.toml exists": (project_root / "pyproject.toml").exists(),
        "README.md exists": (project_root / "README.md").exists(),
        "LICENSE exists": (project_root / "LICENSE").exists(),
        "package directory exists": (project_root / "huoshui_pdf_translator").exists(),
        "__init__.py exists": (project_root / "huoshui_pdf_translator" / "__init__.py").exists(),
        "main.py exists": (project_root / "huoshui_pdf_translator" / "main.py").exists(),
    }

    all_passed = True
    for check, passed in checks.items():
        status = "success" if passed else "error"
        print_status(f"{check}: {'✓' if passed else '✗'}", status)
        if not passed:
            all_passed = False

    return {"all_passed": all_passed, **checks}


def check_version_consistency(project_root: Path) -> bool:
    """Check version consistency between __init__.py and pyproject.toml."""
    print_status("Checking version consistency...", "info")

    # Read version from pyproject.toml
    import tomllib

    with open(project_root / "pyproject.toml", "rb") as f:
        pyproject_data = tomllib.load(f)
    pyproject_version = pyproject_data["project"]["version"]

    # Read version from __init__.py
    init_file = project_root / "huoshui_pdf_translator" / "__init__.py"
    init_content = init_file.read_text()

    # Extract version using regex
    import re

    version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', init_content)
    if not version_match:
        print_status("Could not find __version__ in __init__.py", "error")
        return False

    init_version = version_match.group(1)

    if pyproject_version == init_version:
        print_status(f"Version consistency check passed: {pyproject_version}", "success")
        return True
    else:
        print_status(
            f"Version mismatch: pyproject.toml={pyproject_version}, __init__.py={init_version}",
            "error",
        )
        return False


def validate_dependencies(project_root: Path) -> bool:
    """Validate dependencies are properly declared."""
    print_status("Validating dependencies...", "info")

    # Check if uv.lock exists (indicates dependencies are resolved)
    if (project_root / "uv.lock").exists():
        print_status("uv.lock found - dependencies are resolved", "success")
        return True
    else:
        print_status("uv.lock not found - running dependency resolution", "warning")
        try:
            run_command(["uv", "sync", "--extra", "dev"], "dependency resolution", project_root)
            return True
        except subprocess.CalledProcessError:
            print_status("Dependency resolution failed", "error")
            return False


def clean_build_artifacts(project_root: Path) -> None:
    """Clean previous build artifacts."""
    print_status("Cleaning build artifacts...", "info")

    artifacts_to_clean = [
        project_root / "dist",
        project_root / "build",
        project_root / "*.egg-info",
    ]

    for artifact in artifacts_to_clean:
        if artifact.exists():
            if artifact.is_dir():
                shutil.rmtree(artifact)
                print_status(f"Removed directory: {artifact}", "success")
            else:
                artifact.unlink()
                print_status(f"Removed file: {artifact}", "success")

    # Clean egg-info directories with glob
    for egg_info in project_root.glob("*.egg-info"):
        if egg_info.is_dir():
            shutil.rmtree(egg_info)
            print_status(f"Removed egg-info: {egg_info}", "success")


def run_quality_checks(project_root: Path) -> bool:
    """Run linting and type checking if configured."""
    print_status("Running quality checks...", "info")

    checks_passed = True

    # Check if ruff is configured
    try:
        run_command(
            ["uv", "run", "ruff", "check", "huoshui_pdf_translator/"], "ruff linting", project_root
        )
        print_status("Ruff linting passed", "success")
    except subprocess.CalledProcessError:
        print_status("Ruff linting failed", "warning")
        checks_passed = False
    except FileNotFoundError:
        print_status("Ruff not available, skipping", "warning")

    # Check if black is configured
    try:
        run_command(
            ["uv", "run", "black", "--check", "huoshui_pdf_translator/"],
            "black formatting check",
            project_root,
        )
        print_status("Black formatting check passed", "success")
    except subprocess.CalledProcessError:
        print_status("Black formatting check failed", "warning")
        checks_passed = False
    except FileNotFoundError:
        print_status("Black not available, skipping", "warning")

    return checks_passed


def build_package(project_root: Path) -> Dict[str, Path]:
    """Build wheel and source distributions."""
    print_status("Building package distributions...", "info")

    # Install build dependencies
    run_command(["uv", "sync", "--extra", "dev"], "install build dependencies", project_root)

    # Build the package
    run_command(["uv", "build"], "package build", project_root)

    # Find built files
    dist_dir = project_root / "dist"
    if not dist_dir.exists():
        raise RuntimeError("dist/ directory not created after build")

    built_files = list(dist_dir.glob("*"))
    wheel_files = [f for f in built_files if f.suffix == ".whl"]
    sdist_files = [f for f in built_files if f.suffix == ".gz"]

    print_status(f"Built {len(built_files)} files:", "success")
    for file in built_files:
        size_mb = file.stat().st_size / (1024 * 1024)
        print_status(f"  {file.name} ({size_mb:.1f} MB)", "info")

    return {
        "wheel": wheel_files[0] if wheel_files else None,
        "sdist": sdist_files[0] if sdist_files else None,
        "all_files": built_files,
    }


def test_package_import(project_root: Path) -> bool:
    """Test package import after build."""
    print_status("Testing package import...", "info")

    try:
        # Create a temporary virtual environment and test import
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Install the built wheel for testing
            dist_dir = project_root / "dist"
            wheel_files = list(dist_dir.glob("*.whl"))

            if wheel_files:
                wheel_file = wheel_files[0]
                run_command(
                    [
                        "uv",
                        "run",
                        "--isolated",
                        "--with",
                        str(wheel_file),
                        "python",
                        "-c",
                        "import huoshui_pdf_translator; print(f'Import successful: {huoshui_pdf_translator.__version__}')",
                    ],
                    "test package import",
                    project_root,
                )
                print_status("Package import test passed", "success")
                return True
            else:
                print_status("No wheel file found for testing", "warning")
                return False

    except subprocess.CalledProcessError as e:
        print_status("Package import test failed", "error")
        print(f"Error: {e}")
        return False


def main():
    """Main build script entry point."""
    parser = argparse.ArgumentParser(description="Automated PyPI build script with validation")
    parser.add_argument("--skip-quality-checks", action="store_true", help="Skip quality checks")
    parser.add_argument("--skip-tests", action="store_true", help="Skip import tests")
    parser.add_argument(
        "--version-bump", choices=["patch", "minor", "major"], help="Bump version before build"
    )

    args = parser.parse_args()

    # Find project root
    project_root = Path(__file__).parent.parent
    print_status(f"Building project in: {project_root}", "info")

    try:
        # Phase 1: Pre-build validation
        print_status("\n=== PHASE 1: PRE-BUILD VALIDATION ===", "info")

        structure_check = check_project_structure(project_root)
        if not structure_check["all_passed"]:
            print_status("Project structure validation failed", "error")
            sys.exit(1)

        if not check_version_consistency(project_root):
            print_status("Version consistency check failed", "error")
            sys.exit(1)

        if not validate_dependencies(project_root):
            print_status("Dependency validation failed", "error")
            sys.exit(1)

        # Phase 2: Quality checks
        if not args.skip_quality_checks:
            print_status("\n=== PHASE 2: QUALITY CHECKS ===", "info")
            quality_passed = run_quality_checks(project_root)
            if not quality_passed:
                print_status("Quality checks failed - proceeding with warnings", "warning")

        # Phase 3: Build process
        print_status("\n=== PHASE 3: BUILD PROCESS ===", "info")

        clean_build_artifacts(project_root)
        built_files = build_package(project_root)

        # Phase 4: Post-build testing
        if not args.skip_tests:
            print_status("\n=== PHASE 4: POST-BUILD TESTING ===", "info")
            if not test_package_import(project_root):
                print_status("Package import test failed - build may have issues", "warning")

        # Summary
        print_status("\n=== BUILD COMPLETE ===", "success")
        print_status(f"Built files in {project_root}/dist/:", "success")
        for file in built_files["all_files"]:
            size_mb = file.stat().st_size / (1024 * 1024)
            print_status(f"  {file.name} ({size_mb:.1f} MB)", "info")

        print_status("\nNext steps:", "info")
        print_status("1. Run: python scripts/upload.py --test  # Upload to TestPyPI", "info")
        print_status(
            "2. Test installation: uv add --index-url https://test.pypi.org/simple/ huoshui-pdf-translator",
            "info",
        )
        print_status("3. Run: python scripts/upload.py --prod  # Upload to production PyPI", "info")

    except KeyboardInterrupt:
        print_status("\nBuild cancelled by user", "warning")
        sys.exit(1)
    except Exception as e:
        print_status(f"Build failed with error: {e}", "error")
        sys.exit(1)


if __name__ == "__main__":
    main()
