# PyPI Publishing Workflow Documentation

This document describes the complete automated PyPI publishing workflow for the Huoshui PDF Translator package.

## 🚀 Quick Start

### Option 1: Full Automated Workflow

```bash
# Complete workflow with patch version bump
python scripts/pypi_workflow.py --full-workflow --version-bump patch --force
```

### Option 2: Step-by-Step Workflow

```bash
# 1. Build the package
python scripts/build.py

# 2. Upload to TestPyPI
python scripts/upload.py --test

# 3. Test installation from TestPyPI
uv add --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ huoshui-pdf-translator

# 4. Upload to production PyPI
python scripts/upload.py --prod
```

## 📁 Workflow Scripts

### 1. `scripts/build.py` - Build Automation

Complete build process with validation:

```bash
# Basic build
python scripts/build.py

# Skip quality checks
python scripts/build.py --skip-quality-checks

# Skip import tests
python scripts/build.py --skip-tests

# Version bump and build
python scripts/build.py --version-bump patch
```

**Features:**

- ✅ Project structure validation
- ✅ Version consistency checks
- ✅ Dependency validation
- ✅ Quality checks (ruff, black)
- ✅ Clean build artifacts
- ✅ Generate wheel and source distributions
- ✅ Post-build import testing

### 2. `scripts/upload.py` - Upload Automation

Interactive publishing to PyPI repositories:

```bash
# Upload to TestPyPI
python scripts/upload.py --test

# Upload to production PyPI
python scripts/upload.py --prod

# Skip installation tests
python scripts/upload.py --test --skip-tests

# Force upload without prompts
python scripts/upload.py --prod --force
```

**Features:**

- ✅ Distribution file validation
- ✅ Credential checking
- ✅ Interactive confirmations
- ✅ Repository-specific uploads
- ✅ Post-upload installation testing
- ✅ Progress reporting

### 3. `scripts/pypi_workflow.py` - Workflow Orchestration

Complete workflow automation with intelligent error handling:

```bash
# Build only
python scripts/pypi_workflow.py --build-only

# Test upload workflow
python scripts/pypi_workflow.py --test-upload

# Production upload (requires existing build)
python scripts/pypi_workflow.py --prod-upload

# Complete workflow
python scripts/pypi_workflow.py --full-workflow --version-bump patch
```

**Features:**

- ✅ Orchestrates all workflow steps
- ✅ Version management automation
- ✅ Error recovery and continuation
- ✅ Interactive confirmations
- ✅ Comprehensive status reporting

## 🔧 Workflow Phases

### Phase 1: Pre-Publishing Validation

**Automated Checks:**

1. **Project Structure Analysis**

   - Validates pyproject.toml completeness
   - Checks required package metadata
   - Identifies main package directory

2. **Version Management**

   - Checks version consistency between `__init__.py` and `pyproject.toml`
   - Applies version bump if requested
   - Validates semantic versioning compliance

3. **Dependencies Check**
   - Verifies all dependencies are properly declared
   - Checks for development vs production dependencies
   - Validates Python version requirements

### Phase 2: Configuration & Setup

**Automated Actions:**

1. **Build System Configuration**

   - Ensures build system is properly configured (Hatchling)
   - Validates package metadata completeness
   - Console scripts already configured

2. **Quality Checks**
   - Runs ruff linting if configured
   - Runs black formatting check if configured
   - Validates package structure follows Python standards

### Phase 3: Build Automation

**Automated Process:**

1. **Clean Environment**

   - Removes previous build artifacts
   - Cleans egg-info directories
   - Prepares clean build environment

2. **Build Process**

   - Installs build dependencies via UV
   - Generates wheel and source distributions
   - Reports package sizes and contents

3. **Local Testing**
   - Tests package import after build
   - Validates console scripts functionality
   - Checks for common packaging issues

### Phase 4: Publishing & Validation

**Automated Flow:**

1. **TestPyPI Upload**

   - Uploads to TestPyPI for validation
   - Tests installation from TestPyPI
   - Validates basic functionality

2. **Production Upload**

   - Confirms TestPyPI success before production
   - Uploads to production PyPI
   - Verifies availability

3. **Post-Publishing Validation**
   - Tests installation from production PyPI
   - Validates package functionality
   - Reports installation success metrics

## 🛠️ Configuration Files

### pyproject.toml Configuration

The workflow uses the existing `pyproject.toml` with optimized dependency groups:

```toml
[dependency-groups]
dev = [
    "build>=1.2.2.post1",
    "twine>=6.1.0",
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]
publish = [
    "build>=1.2.2.post1",
    "twine>=6.1.0",
]
```

### UV Integration

All scripts use UV for modern Python package management:

```bash
# Install dependencies
uv sync --group dev

# Build package
uv build

# Run with isolated environment
uv run --isolated python -c "import package"
```

## 🚨 Error Handling & Recovery

### Common Issues & Automated Solutions

1. **Build Failures**

   - **Detection:** Package build process fails
   - **Auto-fix:** Check dependencies, metadata, file inclusion
   - **Validation:** Successful build with no warnings

2. **Upload Failures**

   - **Detection:** PyPI upload rejected or fails
   - **Auto-guidance:** Credential setup, package conflicts, metadata issues
   - **Recovery:** Retry mechanisms with exponential backoff

3. **Installation Issues**

   - **Detection:** Package installs but doesn't work correctly
   - **Auto-test:** Fresh installation validation
   - **Recovery:** Detailed error reporting with solutions

4. **Version Conflicts**
   - **Detection:** Version inconsistencies across files
   - **Auto-fix:** Synchronize version numbers automatically
   - **Validation:** Confirm consistency before build

## 📊 Workflow Status Reporting

The workflow provides comprehensive status reporting:

### Build Status

- ✅ Project structure validation
- ✅ Version consistency check
- ✅ Dependency resolution
- ✅ Quality checks (linting/formatting)
- ✅ Build artifact generation
- ✅ Package size reporting
- ✅ Import validation

### Upload Status

- ✅ Distribution file validation
- ✅ Credential verification
- ✅ Repository upload progress
- ✅ Installation testing
- ✅ Availability confirmation

### Final Report

- 📦 Package name and version
- 🌐 Repository URLs (TestPyPI/PyPI)
- 📁 Generated files and sizes
- ⏱️ Processing times
- 🔗 Installation commands

## 🎯 Best Practices

### Version Management

```bash
# Patch version for bug fixes
python scripts/pypi_workflow.py --full-workflow --version-bump patch

# Minor version for new features
python scripts/pypi_workflow.py --full-workflow --version-bump minor

# Major version for breaking changes
python scripts/pypi_workflow.py --full-workflow --version-bump major
```

### Testing Strategy

```bash
# Always test on TestPyPI first
python scripts/pypi_workflow.py --test-upload

# Validate installation
uv add --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ huoshui-pdf-translator

# Then upload to production
python scripts/pypi_workflow.py --prod-upload
```

### Automation for CI/CD

```bash
# Fully automated workflow for CI/CD
python scripts/pypi_workflow.py --full-workflow --version-bump patch --force --skip-quality-checks
```

## 🔍 Troubleshooting

### Script Permissions

```bash
chmod +x scripts/*.py
```

### Missing Dependencies

```bash
uv sync --group dev
```

### UV Not Installed

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Build Issues

```bash
# Clean and rebuild
rm -rf dist/ build/ *.egg-info
python scripts/build.py
```

### Upload Issues

```bash
# Check credentials
uv run twine check dist/*

# Manual credential setup
uv run twine configure
```

## 📈 Performance Metrics

- **Build Time:** ~30-60 seconds (with quality checks)
- **Upload Time:** ~10-30 seconds (depending on file size)
- **Full Workflow:** ~2-5 minutes (including TestPyPI validation)
- **Package Size:** ~1-5 MB (wheel + source distribution)

## 🔐 Security Considerations

- **Credential Management:** Uses secure credential storage (keyring)
- **Path Validation:** Prevents system directory access
- **Isolated Testing:** Uses UV's isolated environments
- **Repository Validation:** Separate TestPyPI and production workflows

---

This workflow automation provides a robust, tested, and user-friendly approach to PyPI package publishing with comprehensive error handling and recovery mechanisms.
