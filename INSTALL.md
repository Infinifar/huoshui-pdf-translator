# 🚀 Installation Guide

## Quick Start (Recommended)

### Step 1: Install via uvx
```bash
uvx huoshui-pdf-translator
```

### Step 2: Configure Claude Desktop
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

### Step 3: First-Time Setup
1. **Restart Claude Desktop**
2. **Run warmup**: Use `warm_up_translator` tool (downloads assets)
3. **Check status**: Use `check_translation_tool` tool
4. **Start translating**: Use `translate_pdf` tool with your PDF paths

That's it! No local file paths, no complex setup required.

## Alternative Installation Methods

### Via pipx
```bash
pipx install huoshui-pdf-translator
```

### Via UV tools
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

### From Source (Development)
```bash
git clone https://github.com/huoshuiai/huoshui-pdf-translator.git
cd huoshui-pdf-translator
uv sync
uv run python -m huoshui_pdf_translator.main
```

## Configuration Locations

### Claude Desktop Config Files
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

### Complete Example Configuration
```json
{
  "mcpServers": {
    "huoshui-pdf-translator": {
      "command": "uvx",
      "args": ["huoshui-pdf-translator"]
    }
  },
  "globalShortcut": "CommandOrControl+;",
  "allowedLists": ["huoshui-pdf-translator"]
}
```

## Troubleshooting

### Command not found: uvx
```bash
# Install UV first
curl -LsSf https://astral.sh/uv/install.sh | sh
# or
pip install uv
```

### Tools not appearing in Claude Desktop
1. **Check config syntax**: Ensure JSON is valid
2. **Restart Claude Desktop**: Required after config changes  
3. **Check logs**: Look for error messages in Claude Desktop
4. **Verify installation**: Run `uvx huoshui-pdf-translator --help`

### Translation timeout on first use
1. **Run warmup first**: Use `warm_up_translator` tool
2. **Check network**: Internet required for asset downloads
3. **Be patient**: First run downloads ~50MB of fonts/models

### Tool installation issues
```bash
# Check if tool is available
pdf2zh --version

# Manual install if needed
pip install pdf2zh-next
```

## Updates

### Update to latest version
```bash
# Via uvx
uvx install --upgrade huoshui-pdf-translator

# Via UV tools
uv tool upgrade huoshui-pdf-translator

# Via pipx
pipx upgrade huoshui-pdf-translator
```

## Performance Notes

- **First translation**: 2-5 minutes (downloads fonts/models)
- **Subsequent translations**: 30-60 seconds
- **File size limit**: 200MB maximum  
- **Cache location**: `~/.cache/babeldoc/`
- **Cache size**: ~50MB for fonts and models

## Verification

### Test the installation
1. **Check command**: `uvx huoshui-pdf-translator --help`
2. **Verify in Claude Desktop**: Look for translation tools
3. **Run status check**: Use `check_translation_tool` tool
4. **Test with sample PDF**: Use `translate_pdf` tool

### Expected tools in Claude Desktop
- `translate_pdf` - Main translation function
- `pdf_get` - PDF file analysis
- `warm_up_translator` - Asset pre-download
- `check_translation_tool` - Status verification

### Expected prompts
- `role_and_rules` - Assistant configuration
- `explain_pdf_paths` - Path help
- `explain_translation_options` - Translation guidance
- `troubleshoot_translation_error` - Error help
- `explain_translation_result` - Result explanation

## Support

### Common Issues
- **File not found**: Check PDF file path spelling
- **Permission denied**: Ensure file is readable
- **Network issues**: Check internet connection for downloads
- **Tool missing**: Install `pdf2zh-next` manually if needed

### Getting Help
1. **Check status**: Use `check_translation_tool` tool
2. **Use prompts**: Built-in troubleshooting prompts available
3. **Check logs**: Claude Desktop logs for error details
4. **GitHub Issues**: Report problems at project repository

Your PDF translator is ready to use! 📄➡️🌐