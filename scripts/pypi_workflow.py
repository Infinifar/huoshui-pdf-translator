#!/usr/bin/env python3
"""
Complete PyPI Package Workflow Automation
Orchestrates the entire build and publish process with intelligent error handling.
"""

import argparse
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


def print_banner(text: str) -> None:
    """Print a banner with the given text."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'=' * 60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text.center(60)}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'=' * 60}{Colors.END}\n")


def run_script(script_path: Path, args: List[str] = None) -> bool:
    """Run a Python script and return success status."""
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)

    try:
        result = subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"Script failed with exit code {e.returncode}", "error")
        return False


def get_user_confirmation(message: str, default: bool = True) -> bool:
    """Get user confirmation with default value."""
    default_text = "Y/n" if default else "y/N"
    while True:
        response = input(f"{Colors.YELLOW}{message} ({default_text}): {Colors.END}").lower().strip()

        if not response:
            return default
        elif response in ["y", "yes"]:
            return True
        elif response in ["n", "no"]:
            return False
        else:
            print("Please answer 'y' or 'n'")


def bump_version(project_root: Path, bump_type: str) -> str:
    """Bump version in both pyproject.toml and __init__.py."""
    print_status(f"Bumping version ({bump_type})...", "info")

    # Read current version
    import tomllib

    with open(project_root / "pyproject.toml", "rb") as f:
        pyproject_data = tomllib.load(f)

    current_version = pyproject_data["project"]["version"]

    # Parse version
    version_parts = [int(x) for x in current_version.split(".")]
    while len(version_parts) < 3:
        version_parts.append(0)

    # Bump version
    if bump_type == "major":
        version_parts[0] += 1
        version_parts[1] = 0
        version_parts[2] = 0
    elif bump_type == "minor":
        version_parts[1] += 1
        version_parts[2] = 0
    elif bump_type == "patch":
        version_parts[2] += 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")

    new_version = ".".join(map(str, version_parts))

    # Update pyproject.toml
    pyproject_path = project_root / "pyproject.toml"
    content = pyproject_path.read_text()
    content = content.replace(f'version = "{current_version}"', f'version = "{new_version}"')
    pyproject_path.write_text(content)

    # Update __init__.py
    init_path = project_root / "huoshui_pdf_translator" / "__init__.py"
    init_content = init_path.read_text()
    init_content = init_content.replace(
        f'__version__ = "{current_version}"', f'__version__ = "{new_version}"'
    )
    init_path.write_text(init_content)

    print_status(f"Version bumped: {current_version} → {new_version}", "success")
    return new_version


def run_workflow(args):
    """Run the complete PyPI workflow."""
    project_root = Path(__file__).parent.parent
    scripts_dir = project_root / "scripts"

    print_banner("HUOSHUI PDF TRANSLATOR - PYPI WORKFLOW")
    print_status(f"Project root: {project_root}", "info")
    print_status(f"Scripts directory: {scripts_dir}", "info")

    try:
        # Step 1: Version management
        if args.version_bump:
            print_banner("STEP 1: VERSION MANAGEMENT")
            new_version = bump_version(project_root, args.version_bump)
            print_status(f"New version: {new_version}", "success")

        # Step 2: Build process
        print_banner("STEP 2: BUILD PROCESS")
        build_args = []
        if args.skip_quality_checks:
            build_args.append("--skip-quality-checks")
        if args.skip_build_tests:
            build_args.append("--skip-tests")

        build_success = run_script(scripts_dir / "build.py", build_args)
        if not build_success:
            print_status("Build failed, aborting workflow", "error")
            return False

        # Step 3: TestPyPI upload (if requested)
        if args.test_upload or args.full_workflow:
            print_banner("STEP 3: TESTPYPI UPLOAD")

            if not args.force and not get_user_confirmation("Upload to TestPyPI?"):
                print_status("Skipping TestPyPI upload", "warning")
            else:
                upload_args = ["--test"]
                if args.skip_install_tests:
                    upload_args.append("--skip-tests")
                if args.force:
                    upload_args.append("--force")

                test_upload_success = run_script(scripts_dir / "upload.py", upload_args)
                if not test_upload_success:
                    print_status("TestPyPI upload failed", "error")
                    if not args.force and not get_user_confirmation(
                        "Continue with production upload anyway?"
                    ):
                        return False

        # Step 4: Production PyPI upload (if requested)
        if args.prod_upload or args.full_workflow:
            print_banner("STEP 4: PRODUCTION PYPI UPLOAD")

            if not args.force:
                if not get_user_confirmation("Upload to production PyPI?", default=False):
                    print_status("Skipping production PyPI upload", "warning")
                    print_status("Workflow completed up to TestPyPI", "success")
                    return True

            upload_args = ["--prod"]
            if args.skip_install_tests:
                upload_args.append("--skip-tests")
            if args.force:
                upload_args.append("--force")

            prod_upload_success = run_script(scripts_dir / "upload.py", upload_args)
            if not prod_upload_success:
                print_status("Production PyPI upload failed", "error")
                return False

        # Success!
        print_banner("WORKFLOW COMPLETE")
        print_status("PyPI workflow completed successfully! 🎉", "success")

        # Final instructions
        print_status("\nPackage is now available:", "info")
        if args.prod_upload or args.full_workflow:
            print_status("• Production PyPI: uv add huoshui-pdf-translator", "info")
            print_status("• Package URL: https://pypi.org/project/huoshui-pdf-translator/", "info")
        else:
            print_status("• TestPyPI only - use appropriate test installation commands", "info")

        return True

    except KeyboardInterrupt:
        print_status("\nWorkflow cancelled by user", "warning")
        return False
    except Exception as e:
        print_status(f"Workflow failed with error: {e}", "error")
        return False


def main():
    """Main workflow entry point."""
    parser = argparse.ArgumentParser(
        description="Complete PyPI package workflow automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Build only
  %(prog)s --build-only
  
  # Full workflow with version bump
  %(prog)s --full-workflow --version-bump patch
  
  # Test upload only
  %(prog)s --test-upload
  
  # Production upload (requires build first)
  %(prog)s --prod-upload
  
  # Automated full workflow
  %(prog)s --full-workflow --version-bump patch --force
        """,
    )

    # Workflow modes
    workflow_group = parser.add_mutually_exclusive_group(required=True)
    workflow_group.add_argument("--build-only", action="store_true", help="Run build process only")
    workflow_group.add_argument(
        "--test-upload", action="store_true", help="Upload to TestPyPI (requires existing build)"
    )
    workflow_group.add_argument(
        "--prod-upload",
        action="store_true",
        help="Upload to production PyPI (requires existing build)",
    )
    workflow_group.add_argument(
        "--full-workflow",
        action="store_true",
        help="Complete workflow: build → TestPyPI → production PyPI",
    )

    # Version management
    parser.add_argument(
        "--version-bump", choices=["patch", "minor", "major"], help="Bump version before build"
    )

    # Build options
    parser.add_argument(
        "--skip-quality-checks", action="store_true", help="Skip linting and formatting checks"
    )
    parser.add_argument(
        "--skip-build-tests", action="store_true", help="Skip post-build import tests"
    )

    # Upload options
    parser.add_argument(
        "--skip-install-tests", action="store_true", help="Skip installation tests after upload"
    )

    # Automation
    parser.add_argument("--force", action="store_true", help="Skip all confirmation prompts")

    args = parser.parse_args()

    # Validate arguments
    if (args.test_upload or args.prod_upload) and args.version_bump:
        print_status("Version bump can only be used with --build-only or --full-workflow", "error")
        sys.exit(1)

    success = run_workflow(args)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
