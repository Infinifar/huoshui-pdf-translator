# Huoshui PDF Translator

**Version:** 0.1.0  
**Powered by:** FastMCP & PDFMathTranslate-next  
**PyPI Package:** [`huoshui-pdf-translator`](https://pypi.org/project/huoshui-pdf-translator/)

An intelligent PDF translation assistant that specializes in academic papers with mathematical formulas. Built using the FastMCP framework and powered by PDFMathTranslate-next, it provides comprehensive translation capabilities with context-aware assistance.

## 🌟 Features

### Core Translation Capabilities

- **📚 Academic Papers**: Excellent handling of mathematical formulas and equations
- **🔬 Technical Documents**: Preserves formatting and technical terminology
- **🌐 Multi-language Support**: Auto-detection with Chinese ↔ English specialization
- **🎨 Layout Preservation**: Maintains original PDF structure and formatting

### Smart Assistant Features

- **🧠 Context-Aware Prompts**: Multiple specialized prompts for different scenarios
- **🛠️ Tool Status Checking**: Verify translation tool installation and availability
- **📊 PDF Analysis**: Get detailed information about PDF files before translation
- **🔍 Flexible Path Handling**: Support for both absolute and relative file paths
- **⚡ Progress Reporting**: Real-time progress updates during translation
- **🚨 Intelligent Error Handling**: Comprehensive error diagnosis and troubleshooting

### MCP Features

- **📋 Resources**: Translation capability listings and PDF file information
- **🎯 Tools**: Translation, PDF analysis, and tool status checking
- **💬 Prompts**: Role definitions, path guidance, options explanation, and error troubleshooting
- **🔒 Security**: Safe path validation with system directory protection

## 🚀 Quick Start

### Installation (Recommended)

**One-command installation via uvx:**

```bash
uvx huoshui-pdf-translator
```

That's it! No local dependencies, no file paths, no setup required.

### Claude Desktop Setup

Add this to your Claude Desktop MCP configuration:

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

### Alternative Installation Methods

**Via pipx:**
```bash
pipx install huoshui-pdf-translator
```

**Via UV tools:**
```bash
uv tool install huoshui-pdf-translator
```

**Claude Desktop config for UV tools:**
```json
{
  "mcpServers": {
    "huoshui-pdf-translator": {
      "command": "uv",
      "args": ["tool", "run", "huoshui-pdf-translator"]
    }
  }
}
```

## 📖 Usage

### First-Time Setup

1. **Warm up** (downloads fonts/models): Use `warm_up_translator` tool
2. **Check status**: Use `check_translation_tool` tool
3. **Translate**: Use `translate_pdf` tool with your PDF path

### MCP Tools

#### `translate_pdf`

Translates PDF documents while preserving mathematical formulas and layout.

```python
# Basic usage
translate_pdf(pdf_path="Desktop/paper.pdf")

# With custom output path
translate_pdf(
    pdf_path="Documents/research.pdf",
    output_path="Documents/translated/research_cn.pdf"
)
```

#### `pdf_get`

Retrieves detailed information about a PDF file.

```python
pdf_info = pdf_get(path="Desktop/document.pdf")
# Returns: PDFResource with path, size_bytes, page_count
```

#### `warm_up_translator`

Downloads required assets and models. Run this first to avoid timeouts.

```python
warm_up_translator()
# Downloads fonts and models (~50MB) for faster subsequent translations
```

#### `check_translation_tool`

Verifies PDFMathTranslate-next installation and status.

```python
status = check_translation_tool()
# Returns: status, version, message
```

### MCP Prompts

- **`role_and_rules`**: Core identity and operational rules
- **`explain_pdf_paths`**: Help with file path specifications
- **`explain_translation_options`**: Available options and best practices
- **`troubleshoot_translation_error`**: Error diagnosis and solutions
- **`explain_translation_result`**: Result explanation and next steps

### File Path Examples

The assistant supports flexible path specifications:

```bash
# Absolute paths
/Users/john/Desktop/research.pdf
C:\Users\John\Documents\paper.pdf

# Relative to home directory
Desktop/research.pdf
Documents/papers/study.pdf

# Simple filenames (assumes home directory)
paper.pdf
```

## 🎯 Translation Workflow

1. **Install**: `uvx huoshui-pdf-translator`
2. **Setup Claude Desktop**: Add MCP configuration
3. **Warm up**: Run `warm_up_translator` tool (first time only)
4. **Translate**: Use `translate_pdf` with your PDF path
5. **Review**: Two files created (dual-language and Chinese-only)

## ⚡ Performance

- **First translation**: 2-5 minutes (downloads fonts/models)
- **Subsequent translations**: 30-60 seconds
- **File size limit**: 200MB maximum
- **Cache size**: ~50MB for fonts and models

## 🔍 Troubleshooting

### Common Issues

#### Translation Tool Not Available
The tool automatically installs `pdf2zh-next` when needed. If issues occur:
```bash
# Check status
# Use check_translation_tool in Claude Desktop

# Manual install if needed
pip install pdf2zh-next
```

#### First Translation Timeout
```bash
# Run warmup first
# Use warm_up_translator tool in Claude Desktop
```

#### PDF File Not Found
- Verify file path is correct
- Use absolute paths for clarity
- Check file hasn't been moved or deleted

#### Network Issues
- Ensure internet connection (required for first-time font downloads)
- Check firewall settings

### Error Diagnosis

The assistant provides intelligent error diagnosis with specific solutions for:
- File not found errors
- Invalid PDF files
- Translation tool issues
- Network connectivity problems
- File size limitations

## 🛠️ Development

### For Developers

**Install from source:**
```bash
git clone https://github.com/huoshuiai/huoshui-pdf-translator.git
cd huoshui-pdf-translator
uv sync
uv run python -m huoshui_pdf_translator.main
```

**Build and publish:**
```bash
uv build
uv run twine upload dist/*
```

### Project Structure

```
huoshui-pdf-translator/
├── huoshui_pdf_translator/
│   ├── __init__.py      # Package metadata
│   └── main.py         # FastMCP server implementation
├── pyproject.toml      # Package configuration
├── README.md          # This file
└── LICENSE           # Apache-2.0 license
```

## 🔄 Updates

**Update to latest version:**
```bash
uvx install --upgrade huoshui-pdf-translator
# or
uv tool upgrade huoshui-pdf-translator
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the Apache-2.0 License. See the LICENSE file for details.

## 🙏 Acknowledgments

- **PDFMathTranslate-next**: Core translation engine
- **FastMCP**: Framework for intelligent assistant capabilities  
- **Anthropic**: MCP protocol and ecosystem
- **UV & PyPI**: Modern Python packaging and distribution