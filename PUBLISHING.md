# PyPI Publishing Guide - Huoshui PDF Translator

Complete guide for publishing the Huoshui PDF Translator to PyPI with automated workflows.

## 🎯 Quick Publishing Commands

### One-Command Publishing

```bash
# Patch version bump + full workflow
make patch

# Minor version bump + full workflow
make minor

# Major version bump + full workflow
make major
```

### Step-by-Step Publishing

```bash
# 1. Build package
make build

# 2. Upload to TestPyPI
make test-upload

# 3. Test installation
make test-install

# 4. Upload to production PyPI
make prod-upload
```

### Manual Script Usage

```bash
# Complete automated workflow
python scripts/pypi_workflow.py --full-workflow --version-bump patch

# Just build
python scripts/build.py

# Just upload to TestPyPI
python scripts/upload.py --test

# Just upload to production
python scripts/upload.py --prod
```

## 📦 Package Information

- **Package Name**: `huoshui-pdf-translator`
- **Current Version**: `0.1.1`
- **PyPI URL**: https://pypi.org/project/huoshui-pdf-translator/
- **Repository**: https://github.com/huoshuiai/huoshui-pdf-translator

## 🔧 Prerequisites

### Required Tools

```bash
# Install UV (modern Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install development dependencies
make install
# or
uv sync --all-extras
```

### PyPI Credentials

Set up PyPI API tokens:

```bash
# For production PyPI
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-api-token-here

# For TestPyPI (optional)
export TWINE_REPOSITORY=testpypi
export TWINE_PASSWORD=pypi-your-test-api-token-here
```

Or configure via keyring:

```bash
uv run twine configure
```

## 🚀 Publishing Workflows

### Workflow 1: Quick Patch Release

For bug fixes and minor updates:

```bash
# Automated patch release
make patch
```

This will:

1. Bump patch version (0.1.1 → 0.1.2)
2. Build package with validation
3. Upload to TestPyPI
4. Test installation
5. Upload to production PyPI

### Workflow 2: Feature Release

For new features:

```bash
# Minor version release
make minor
```

This will:

1. Bump minor version (0.1.1 → 0.2.0)
2. Run full workflow with testing

### Workflow 3: Manual Control

For custom workflow control:

```bash
# 1. Build only
python scripts/build.py

# 2. Check build quality
ls -la dist/
uv run twine check dist/*

# 3. Upload to TestPyPI first
python scripts/upload.py --test

# 4. Test installation from TestPyPI
uv add --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ huoshui-pdf-translator

# 5. Test the installed package
huoshui-pdf-translator --help  # or your test command

# 6. If tests pass, upload to production
python scripts/upload.py --prod
```

### Workflow 4: CI/CD Automation

For GitHub Actions:

```bash
# Trigger via tag
git tag v0.1.2
git push origin v0.1.2

# Or manual workflow dispatch
# (Use GitHub web interface or gh CLI)
```

## 📋 Pre-Publishing Checklist

### Code Quality

- [ ] All tests pass: `make check`
- [ ] Code is formatted: `make format`
- [ ] Linting passes: `make lint`
- [ ] Version is bumped appropriately

### Package Validation

- [ ] Package builds successfully: `make build`
- [ ] Distribution files exist in `dist/`
- [ ] Package imports correctly after build
- [ ] Console scripts work correctly

### Documentation

- [ ] README.md is up to date
- [ ] Version numbers match across files
- [ ] CHANGELOG.md includes new changes
- [ ] Installation instructions are correct

## 🔍 Testing Your Package

### Local Testing

```bash
# Build and test import
make build
cd /tmp
uv add --find-links /path/to/your/project/dist huoshui-pdf-translator
python -c "import huoshui_pdf_translator; print(huoshui_pdf_translator.__version__)"
```

### TestPyPI Testing

```bash
# Install from TestPyPI
uv add --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ huoshui-pdf-translator

# Test functionality
huoshui-pdf-translator --help
```

### Production Testing

```bash
# Install from production PyPI
uv add huoshui-pdf-translator

# Verify installation
python -c "import huoshui_pdf_translator; print('Success!')"
```

## 🐛 Troubleshooting

### Build Issues

**Problem**: Build fails with dependency errors

```bash
# Solution: Clean and rebuild
make clean
uv sync --all-extras
make build
```

**Problem**: Version inconsistency detected

```bash
# Solution: Fix manually or use version bump
python scripts/pypi_workflow.py --build-only --version-bump patch
```

### Upload Issues

**Problem**: Package already exists on PyPI

```
ERROR: File already exists
```

**Solution**: Version must be unique - bump version first

**Problem**: Authentication failed

```bash
# Check credentials
echo $TWINE_USERNAME
echo $TWINE_PASSWORD

# Or reconfigure
uv run twine configure
```

**Problem**: TestPyPI upload succeeds but production fails

```bash
# Common issue: missing dependencies on PyPI vs TestPyPI
# Solution: Check dependency availability on both repositories
```

### Installation Issues

**Problem**: Package installs but import fails

```bash
# Debug import issues
python -c "import sys; print(sys.path)"
python -c "import huoshui_pdf_translator; print(huoshui_pdf_translator.__file__)"
```

**Problem**: Console scripts not working

```bash
# Check script installation
which huoshui-pdf-translator
python -m huoshui_pdf_translator.main
```

## 📊 Package Statistics

Current package information:

- **Wheel size**: ~20 KB
- **Source distribution**: ~30 KB
- **Dependencies**: 3 main packages (fastmcp, pdf2zh-next, pydantic)
- **Python versions**: >=3.12
- **Build time**: ~30-60 seconds

## 🔒 Security Best Practices

### API Token Management

- Store tokens as environment variables
- Use separate tokens for TestPyPI and production
- Rotate tokens regularly
- Never commit tokens to version control

### Package Signing

```bash
# Sign releases with GPG (optional)
git tag -s v0.1.2 -m "Release version 0.1.2"
```

### Dependency Management

- Pin dependency versions in production
- Regular security audits: `uv audit`
- Use trusted PyPI sources only

## 📈 Release Strategy

### Semantic Versioning

- **Patch** (0.1.1 → 0.1.2): Bug fixes, documentation
- **Minor** (0.1.1 → 0.2.0): New features, backwards compatible
- **Major** (0.1.1 → 1.0.0): Breaking changes

### Release Schedule

- Patch releases: As needed for critical fixes
- Minor releases: Monthly for feature additions
- Major releases: Quarterly or for breaking changes

### Changelog Management

Update `CHANGELOG.md` before each release:

```markdown
## [0.1.2] - 2025-01-XX

### Added

- New feature descriptions

### Fixed

- Bug fix descriptions

### Changed

- Changes that might affect users
```

---

This guide ensures reliable, repeatable PyPI publishing with comprehensive validation and testing at each step.
