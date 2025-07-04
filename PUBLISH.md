# Publishing to PyPI Guide

## ✅ Setup Complete

Your FastMCP PDF translator is now ready for PyPI publishing!

## 📦 What's Ready

### Package Structure
```
huoshui_pdf_translator/
├── __init__.py          # Package metadata and exports
└── main.py             # FastMCP server with main() entry point
```

### Console Script
- **Command**: `huoshui-pdf-translator`
- **Entry Point**: `huoshui_pdf_translator.main:main`
- **Works with**: `uvx huoshui-pdf-translator`

### Dependencies
- **Runtime**: fastmcp, pdf2zh-next, pydantic
- **Dev**: build, twine (for publishing)

## 🚀 Publishing Steps

### 1. Create PyPI Account
```bash
# Register at https://pypi.org/account/register/
# Get API token from https://pypi.org/manage/account/token/
```

### 2. Configure Authentication
```bash
# Option A: Store token in ~/.pypirc
cat > ~/.pypirc << EOF
[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE
EOF

# Option B: Use environment variable
export TWINE_PASSWORD=pypi-YOUR_TOKEN_HERE
```

### 3. Build and Upload
```bash
# Clean previous builds
rm -rf dist/

# Build package
uv build

# Upload to PyPI
uv run twine upload dist/*

# Or upload to TestPyPI first
uv run twine upload --repository testpypi dist/*
```

## 👥 User Installation

### Global Installation (Recommended)
```bash
# Install via uvx (no local dependencies)
uvx huoshui-pdf-translator

# Or via pipx
pipx install huoshui-pdf-translator
```

### Claude Desktop Configuration
```json
{
  "mcpServers": {
    "huoshui-pdf-translator": {
      "command": "uvx",
      "args": ["huoshui-pdf-translator"]
    }
  }
}
```

### Alternative: UV Tool Install
```bash
# Install as UV tool
uv tool install huoshui-pdf-translator

# Claude Desktop config
{
  "mcpServers": {
    "huoshui-pdf-translator": {
      "command": "uv",
      "args": ["tool", "run", "huoshui-pdf-translator"]
    }
  }
}
```

## 🔄 Update Workflow

### Version Updates
1. Update version in `pyproject.toml`
2. Update version in `__init__.py`
3. Build and upload: `uv build && uv run twine upload dist/*`

### User Updates
```bash
# Update global installation
uvx install --upgrade huoshui-pdf-translator

# Or via UV tools
uv tool upgrade huoshui-pdf-translator
```

## 🎯 Benefits vs Other Approaches

### ✅ PyPI + uvx Advantages
- **Zero local paths** - No file system dependencies
- **Automatic updates** - Users can upgrade easily
- **Cross-platform** - Works on all systems
- **Professional** - Standard Python package distribution
- **No git cloning** - Simple one-command install

### vs DXT Extension
- **Simpler**: No DXT toolchain needed
- **Wider reach**: Works with any MCP client
- **Standard tooling**: Uses Python packaging ecosystem

### vs GitHub Direct
- **No git needed**: Users don't need git/GitHub access
- **Version management**: PyPI handles versioning
- **Discovery**: Searchable on PyPI

## 🔧 Testing Before Publishing

### Local Testing
```bash
# Test built package locally
uv tool install ./dist/huoshui_pdf_translator-0.1.0-py3-none-any.whl

# Verify console script works
huoshui-pdf-translator

# Test in Claude Desktop with uvx config
```

### TestPyPI Testing
```bash
# Upload to test index first
uv run twine upload --repository testpypi dist/*

# Test install from TestPyPI
uvx --index-url https://test.pypi.org/simple/ huoshui-pdf-translator
```

## 📈 Next Steps

1. **Create PyPI account** and get API token
2. **Test upload** to TestPyPI first
3. **Upload to PyPI** when ready
4. **Update documentation** with installation instructions
5. **Share with community** - announce on relevant forums/social media

Your MCP server is now ready for professional distribution! 🎉