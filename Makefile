# Huoshui PDF Translator - PyPI Workflow Makefile
# Convenient shortcuts for common workflow tasks

.PHONY: help build test-upload prod-upload full-workflow clean install lint format check

# Default help target
help:
	@echo "Huoshui PDF Translator - PyPI Workflow"
	@echo ""
	@echo "Available targets:"
	@echo "  help         - Show this help message"
	@echo "  install      - Install development dependencies"
	@echo "  setup-pypi   - Setup ~/.pypirc configuration for PyPI"
	@echo "  lint         - Run linting with ruff"
	@echo "  format       - Format code with black"
	@echo "  check        - Run quality checks (lint + format check)"
	@echo "  build        - Build package distributions"
	@echo "  build-fast   - Build package (skip quality checks)"
	@echo "  test-upload  - Upload to TestPyPI"
	@echo "  prod-upload  - Upload to production PyPI"
	@echo "  full-workflow - Complete workflow (build + test + prod)"
	@echo "  patch        - Patch version bump + full workflow"
	@echo "  minor        - Minor version bump + full workflow"
	@echo "  major        - Major version bump + full workflow"
	@echo "  clean        - Clean build artifacts"
	@echo ""
	@echo "Examples:"
	@echo "  make patch           # Bump patch version and publish"
	@echo "  make build           # Build package only"
	@echo "  make test-upload     # Upload to TestPyPI"
	@echo ""

# Development setup
install:
	uv sync --all-extras
	@echo "✅ Development dependencies installed"

# PyPI setup
setup-pypi:
	python scripts/setup_pypirc.py
	@echo "✅ PyPI configuration complete"

# Code quality
lint:
	uv run ruff check huoshui_pdf_translator/
	@echo "✅ Linting complete"

format:
	uv run black huoshui_pdf_translator/
	@echo "✅ Code formatted"

check: lint
	uv run black --check huoshui_pdf_translator/
	@echo "✅ Quality checks passed"

# Build targets
build:
	python scripts/build.py
	@echo "✅ Package build complete"

build-fast:
	python scripts/build.py --skip-quality-checks
	@echo "✅ Fast package build complete"

# Upload targets
test-upload:
	python scripts/upload.py --test
	@echo "✅ TestPyPI upload complete"

prod-upload:
	python scripts/upload.py --prod
	@echo "✅ Production PyPI upload complete"

# Workflow targets
full-workflow:
	python scripts/pypi_workflow.py --full-workflow
	@echo "✅ Full workflow complete"

# Version bump workflows
patch:
	python scripts/pypi_workflow.py --full-workflow --version-bump patch
	@echo "✅ Patch version workflow complete"

minor:
	python scripts/pypi_workflow.py --full-workflow --version-bump minor
	@echo "✅ Minor version workflow complete"

major:
	python scripts/pypi_workflow.py --full-workflow --version-bump major
	@echo "✅ Major version workflow complete"

# Automated workflows (for CI/CD)
auto-patch:
	python scripts/pypi_workflow.py --full-workflow --version-bump patch --force
	@echo "✅ Automated patch workflow complete"

auto-minor:
	python scripts/pypi_workflow.py --full-workflow --version-bump minor --force
	@echo "✅ Automated minor workflow complete"

auto-major:
	python scripts/pypi_workflow.py --full-workflow --version-bump major --force
	@echo "✅ Automated major workflow complete"

# Utility targets
clean:
	rm -rf dist/ build/ *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "✅ Build artifacts cleaned"

# Test installation from TestPyPI
test-install:
	uv add --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ huoshui-pdf-translator
	@echo "✅ Test installation from TestPyPI complete"

# Validation targets
validate:
	python scripts/build.py --skip-tests
	uv run twine check dist/*
	@echo "✅ Package validation complete"

# Quick development workflow
dev: install format lint build
	@echo "✅ Development workflow complete"
