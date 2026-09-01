import asyncio
import os
import subprocess
import time
from pathlib import Path
from typing import Annotated

from fastmcp import Context, FastMCP
from fastmcp.exceptions import ToolError
from pydantic import BaseModel, Field

# Initialize server
mcp = FastMCP("huoshui-pdf-translator")

# =============================================================================
# 可配置项：翻译服务（默认走 pdf2zh_next 已保存的配置，即 GUI 里配的 Ollama）
# =============================================================================
# pdf2zh_next 命令名（新版是 pdf2zh_next，旧版是 pdf2zh）
PDF2ZH_CMD = os.environ.get("PDF2ZH_CMD", "pdf2zh_next")
# 额外参数：如需强制指定 Ollama 服务，可设置环境变量，例如 "--service ollama"
PDF2ZH_EXTRA_ARGS = os.environ.get("PDF2ZH_EXTRA_ARGS", "").split()

# =============================================================================
# DATA MODELS
# =============================================================================

class PDFResource(BaseModel):
    """PDF file resource representation"""
    path: str = Field(description="PDF file path (absolute or relative to home directory)")
    size_bytes: int = Field(description="File size in bytes")
    page_count: int = Field(description="Number of pages in the PDF", default=0)

class TranslationCapability(BaseModel):
    """Translation capability resource"""
    id: str = Field(description="Unique identifier for translation capability")
    source_type: str = Field(description="Source document type")
    target_languages: list[str] = Field(description="Supported target languages")
    method: str = Field(description="Translation method/engine")

# Supported translation capabilities
TRANSLATION_CAPABILITIES = [
    TranslationCapability(
        id="pdf-math-translate",
        source_type="pdf",
        target_languages=["chinese", "english", "auto-detect"],
        method="PDFMathTranslate-next"
    ),
]

def _validate_path(file_path: str) -> Path:
    """
    Validate and resolve file path with basic security checks
    Supports both absolute and relative paths for user convenience
    """
    if os.path.isabs(file_path):
        resolved_path = Path(file_path).resolve()
    else:
        resolved_path = (Path.home() / file_path).resolve()

    restricted_dirs = {
        '/etc', '/sys', '/proc', '/dev', '/boot', '/root',
        '/System', '/Library/System', '/private/etc',
        'C:\\Windows', 'C:\\Program Files', 'C:\\Program Files (x86)',
        'C:\\System32', 'C:\\Windows\\System32'
    }

    resolved_str = str(resolved_path)
    for restricted in restricted_dirs:
        if resolved_str.startswith(restricted):
            raise ToolError(f"Access to system directory not allowed: {restricted}", -32602)

    return resolved_path

def _validate_pdf_file(file_path: Path) -> None:
    """Validate that the file is a PDF"""
    if not file_path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    if not file_path.is_file():
        raise ToolError(f"Path is not a file: {file_path}", -32602)

    if file_path.suffix.lower() != ".pdf":
        raise ToolError(f"File is not a PDF: {file_path.suffix}", -32001)

def _get_pdf_info(file_path: Path) -> dict[str, int]:
    """Get basic PDF information like page count"""
    try:
        result = subprocess.run(
            ["pdfinfo", str(file_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'Pages:' in line:
                    return {"page_count": int(line.split(':')[1].strip())}
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        pass

    try:
        import fitz  # PyMuPDF
        doc = fitz.open(str(file_path))
        page_count = len(doc)
        doc.close()
        return {"page_count": page_count}
    except ImportError:
        pass
    except Exception:
        pass

    return {"page_count": 0}

# =============================================================================
# PROMPTS
# =============================================================================

@mcp.prompt
def role_and_rules() -> str:
    """
    Core identity and operational rules for the PDF translation assistant
    """
    return """
# Your Identity and Core Mission
You are a specialized PDF Translation Assistant powered by PDFMathTranslate-next. Your primary goal is to help users translate PDF documents, especially those containing mathematical formulas and academic content.

# File Path Handling
1. **Flexible Path Support**: You can work with PDF files anywhere on the user's system
   - **Absolute paths**: `/Users/name/Documents/paper.pdf`, `C:\\Users\\Name\\Desktop\\document.pdf`
   - **Relative paths**: `Documents/paper.pdf`, `Desktop/document.pdf` (relative to user's home directory)
   - **Simple names**: `paper.pdf` (assumes file is in user's home directory)

2. **Path Examples**:
   - ✅ `/Users/john/Desktop/research.pdf` (absolute path)
   - ✅ `Desktop/research.pdf` (relative to home)
   - ✅ `research.pdf` (in home directory)
   - ✅ `~/Documents/paper.pdf` (tilde expansion supported)

3. **Security**: Access to system directories (like /etc, /System, C:\\Windows) is restricted for safety.

# Translation Capabilities
- **Academic Papers**: Excellent handling of mathematical formulas and equations
- **Technical Documents**: Preserves formatting and technical terminology
- **Multi-language Support**: Auto-detection or manual language specification
- **Layout Preservation**: Maintains original PDF structure and formatting

# Operational Protocol
- **Translate and Report**: When using `translate_pdf`, the tool returns the path of the translated file
- **Progress Updates**: Real-time progress reporting during translation
- **Quality Assurance**: Verify PDF integrity before and after translation
- **Handle Errors Gracefully**: Provide helpful guidance for common issues
- **File Size Awareness**: Large PDFs may take longer to process

# User Experience
- Ask users for the full file path if they just mention "this PDF" or "the document"
- Suggest common locations like Desktop, Documents, Downloads if users need help
- Provide estimated processing time based on PDF size and complexity
- Explain translation options and recommend best practices
"""

@mcp.prompt
def explain_pdf_paths(user_os: str = "windows") -> str:
    """Help users understand how to specify PDF file paths correctly"""
    if user_os.lower() in ["mac", "macos", "darwin"]:
        return """
# How to Specify PDF File Paths 📄

Here are easy ways to tell me where your PDF is located:

## ✅ **Recommended Methods**:
1. **Relative to home**: `Desktop/document.pdf`, `Documents/paper.pdf`, `Downloads/file.pdf`
2. **Full absolute path**: `/Users/YourName/Documents/research.pdf`
3. **Tilde shortcut**: `~/Desktop/paper.pdf` (~ means your home directory)

## 📍 **Common PDF Locations**:
- `Desktop/filename.pdf` - PDFs on your Desktop
- `Documents/filename.pdf` - PDFs in Documents folder
- `Downloads/filename.pdf` - Downloaded PDFs

## 💡 **Pro Tips**:
- **Get exact path**: Right-click PDF in Finder → "Copy as Pathname"
- **Avoid spaces**: Use quotes around paths with spaces: `"Desktop/My Paper.pdf"`

**Example**: If you have a paper called "research.pdf" on your Desktop, just say: `Desktop/research.pdf`
"""
    else:  # Windows
        return """
# How to Specify PDF File Paths 📄

Here are easy ways to tell me where your PDF is located:

## ✅ **Recommended Methods**:
1. **Full absolute path**: `C:\\Users\\YourName\\Documents\\research.pdf`
2. **Relative to home**: `Desktop\\document.pdf`, `Documents\\paper.pdf`

## 📍 **Common PDF Locations**:
- `Desktop\\filename.pdf` - PDFs on your Desktop
- `Documents\\filename.pdf` - PDFs in Documents folder
- `Downloads\\filename.pdf` - Downloaded PDFs

## 💡 **Pro Tips**:
- **Get exact path**: Right-click PDF in Explorer → "Copy as path"
- **Use forward slashes**: You can also use `/` instead of `\\`

**Example**: If you have a paper called "research.pdf" on your Desktop, say: `C:\\Users\\YourName\\Desktop\\research.pdf`
"""

@mcp.prompt
def explain_translation_options() -> str:
    """Explain available translation options and best practices"""
    return """
# PDF Translation Options 🌐

## 🎯 **Translation Modes**:
- **Auto-detect**: Automatically detects source language (recommended)
- **Chinese ↔ English**: Bilingual academic translation
- **Preserve Math**: Keeps mathematical formulas intact
- **Layout Retention**: Maintains original PDF structure

## 📚 **Best For**:
- **Academic Papers**: Research papers with equations and formulas
- **Technical Documents**: Engineering, physics, mathematics papers
- **Scientific Articles**: Journal articles with complex formatting

## ⚡ **Processing Tips**:
- **File Size**: Larger PDFs (>50MB) take longer to process
- **Complexity**: Pages with many formulas require more time

**Ready to translate? Just provide the PDF path and I'll get started!**
"""

@mcp.prompt
def troubleshoot_translation_error(error_type: str, file_path: str = "", details: str = "") -> str:
    """Provide helpful guidance for common translation errors"""

    error_messages = {
        "file_not_found": f"""
# 🔍 PDF File Not Found

I couldn't locate: `{file_path}`

## Quick Solutions:
1. **Check spelling** - Verify the filename and path are correct
2. **Use full path** - Try the complete path from your file manager
3. **Check extension** - Ensure the file ends with `.pdf`

{details}
""",
        "not_pdf": f"""
# ⚠️ Invalid PDF File

The file doesn't appear to be a valid PDF document.

## ✅ Checklist:
- **File extension**: Must end with `.pdf`

{details}
""",
        "translation_tool_missing": f"""
# 🛠️ Translation Tool Not Available

The PDFMathTranslate-next tool is not installed or not found.

## Installation Required:
```bash
pip install pdf2zh-next
```

{details}
""",
        "translation_failed": f"""
# ⚠️ Translation Failed

The translation process encountered an error.

## Common Causes:
1. **Scanned PDF**: Images instead of selectable text
2. **Corrupted PDF**: File might be damaged
3. **Service Not Configured**: Check Ollama / translation service config

{details}
"""
    }

    return error_messages.get(error_type, f"""
# 🤔 Unexpected Translation Issue

Something unusual happened during the translation process.

{details}
""")

@mcp.prompt
def explain_translation_result(original_file: str, translated_file: str, processing_time: float = 0) -> str:
    """Explain translation results clearly and provide next steps"""

    time_info = f" in {processing_time:.1f} seconds" if processing_time > 0 else ""

    return f"""
# ✅ PDF Translation Complete!

Your PDF has been successfully translated{time_info}.

## File Details:
- **Original PDF**: `{original_file}`
- **Translated PDF**: `{translated_file}`
- **Location**: Same folder as the original PDF
- **Status**: Ready to view!

## What's Next:
- **Open the PDF**: Double-click to view the translated document
- **Compare**: Open both files side-by-side to compare
- **Original preserved**: Your original PDF is completely unchanged

**Enjoy your translated PDF!** 🎉
"""

# =============================================================================
# RESOURCES
# =============================================================================

@mcp.tool
def pdf_get(
    path: Annotated[str, Field(description="PDF file path (absolute or relative to home directory)")]
) -> PDFResource:
    """
    Retrieves detailed information about a PDF file.

    Args:
        path: PDF file path (absolute or relative to home directory)

    Returns:
        PDF resource with detailed information
    """
    try:
        file_path = _validate_path(path)
        _validate_pdf_file(file_path)

        pdf_info = _get_pdf_info(file_path)

        return PDFResource(
            path=str(file_path).replace('\\', '/'),
            size_bytes=file_path.stat().st_size,
            page_count=pdf_info.get("page_count", 0)
        )

    except FileNotFoundError:
        raise
    except Exception as e:
        if isinstance(e, ToolError):
            raise
        raise ToolError(f"Error getting PDF info: {e}", -32099) from e

@mcp.resource(uri="resource://translation_capability_list")
def translation_capability_list() -> list[TranslationCapability]:
    """
    Provides a complete list of all PDF translation capabilities this server supports.
    """
    return TRANSLATION_CAPABILITIES

# =============================================================================
# TOOLS
# =============================================================================

@mcp.tool
async def translate_pdf(
    pdf_path: Annotated[str, Field(description="PDF file path (absolute or relative to home directory)")],
    output_path: Annotated[str, Field(description="Optional output path for translated PDF")] = None,
    lang_out: Annotated[str, Field(description="Target language, e.g. zh-CN, en")] = "zh-CN",
    ctx: Context = None
) -> dict[str, str]:
    """
    Translates a PDF document using PDFMathTranslate-next. Preserves mathematical formulas and layout.

    Args:
        pdf_path: PDF file path (absolute or relative to home directory)
        output_path: Optional custom output path for the translated PDF
        lang_out: Target language code (default zh-CN)

    Returns:
        Dictionary with paths to translated files (dual and mono versions)
    """
    start_time = time.time()

    try:
        if ctx:
            await ctx.info("Starting PDF translation process")

        pdf_file = _validate_path(pdf_path)
        _validate_pdf_file(pdf_file)

        file_size = pdf_file.stat().st_size
        file_size_mb = file_size / (1024 * 1024)

        if file_size > 200 * 1024 * 1024:  # 200MB limit
            raise ToolError(f"PDF too large: {file_size_mb:.1f}MB (limit: 200MB)", -32002)

        if ctx:
            await ctx.report_progress(10, 100)

        if output_path:
            output_dir = _validate_path(output_path)
            if output_dir.is_file():
                output_dir = output_dir.parent
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = pdf_file.parent

        # pdf2zh_next 输出文件命名：<stem>-dual.pdf 和 <stem>-mono.pdf
        expected_dual_file = output_dir / f"{pdf_file.stem}-dual.pdf"
        expected_mono_file = output_dir / f"{pdf_file.stem}-mono.pdf"

        if ctx:
            await ctx.info(f"Output will be saved to: {output_dir}")
            await ctx.report_progress(20, 100)

        # pdf2zh_next 命令：pdf2zh_next <file> --output <dir> --lang-out <lang>
        command = [PDF2ZH_CMD, str(pdf_file), "--output", str(output_dir), "--lang-out", lang_out]
        if PDF2ZH_EXTRA_ARGS:
            command.extend(PDF2ZH_EXTRA_ARGS)

        try:
            if ctx:
                await ctx.info("Starting PDF translation")
                await ctx.report_progress(30, 100)

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            elapsed_time = 0
            while process.poll() is None:
                await asyncio.sleep(5)
                elapsed_time += 5

                if ctx:
                    if elapsed_time <= 30:
                        await ctx.info(f"Initializing translation engine... ({elapsed_time}s)")
                    elif elapsed_time <= 120:
                        await ctx.info(f"Analyzing document layout... ({elapsed_time}s)")
                    else:
                        await ctx.info(f"Translating content... ({elapsed_time}s)")
                    await ctx.report_progress(min(85, 30 + elapsed_time // 5), 100)

                # Timeout after 60 minutes（大文件翻译时间较长）
                if elapsed_time > 3600:
                    process.terminate()
                    raise ToolError("Translation timeout after 60 minutes", -32408)

            stdout, stderr = process.communicate()

            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, command, stdout, stderr)

            if ctx:
                await ctx.report_progress(90, 100)

        except FileNotFoundError as e:
            raise ToolError(
                f"The '{PDF2ZH_CMD}' command was not found. Please install it with: pip install pdf2zh-next",
                -32404
            ) from e
        except subprocess.TimeoutExpired as e:
            raise ToolError(
                "Translation timeout. The PDF might be too complex or large.",
                -32408
            ) from e
        except subprocess.CalledProcessError as e:
            error_details = (e.stderr or e.stdout or "No output from command.")[-2000:]
            raise ToolError(f"Translation command failed: {error_details}", -32099) from e

        created_files = []
        if expected_dual_file.exists():
            created_files.append(str(expected_dual_file))
        if expected_mono_file.exists():
            created_files.append(str(expected_mono_file))

        if not created_files:
            raise ToolError("Translation completed but no output files were created", -32099)

        processing_time = time.time() - start_time

        if ctx:
            await ctx.report_progress(100, 100)
            await ctx.info(f"Translation completed successfully in {processing_time:.1f} seconds")

        return {
            "translated_pdf_path": created_files[0] if created_files else None,
            "dual_pdf_path": str(expected_dual_file) if expected_dual_file.exists() else None,
            "mono_pdf_path": str(expected_mono_file) if expected_mono_file.exists() else None,
            "all_files": ", ".join([Path(f).name for f in created_files])
        }

    except FileNotFoundError:
        raise
    except ToolError:
        raise
    except Exception as e:
        raise ToolError(f"Internal translation error: {e}", -32099) from e

@mcp.tool
async def warm_up_translator(ctx: Context = None) -> dict[str, str]:
    """
    Warm up the PDF translator by downloading required assets and models.
    Run this first to avoid timeouts during actual translation.

    Returns:
        Dictionary with warmup status information
    """
    try:
        if ctx:
            await ctx.info("Starting translator warmup - downloading fonts and models")

        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as dummy_pdf:
            dummy_pdf.write(b'%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n195\n%%EOF')
            dummy_pdf_path = dummy_pdf.name

        try:
            result = subprocess.run(
                [PDF2ZH_CMD, dummy_pdf_path, "--warmup"],
                capture_output=True,
                text=True,
                timeout=600
            )
        finally:
            try:
                os.unlink(dummy_pdf_path)
            except Exception:
                pass

        if result.returncode == 0:
            if ctx:
                await ctx.info("Warmup completed successfully")
            return {
                "status": "success",
                "message": "Translator warmup completed - ready for fast translations"
            }
        else:
            return {
                "status": "error",
                "message": f"Warmup failed: {result.stderr[-500:]}"
            }

    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "message": "Warmup timed out after 10 minutes"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Warmup error: {e}"
        }

@mcp.tool
def check_translation_tool() -> dict[str, str]:
    """
    Checks if the PDFMathTranslate-next tool is properly installed and available.

    Returns:
        Dictionary with status information about the translation tool
    """
    try:
        result = subprocess.run(
            [PDF2ZH_CMD, "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            version_info = result.stdout.strip() or "Available"
            return {
                "status": "available",
                "version": version_info,
                "message": "pdf2zh-next is properly installed and ready to use"
            }
        else:
            return {
                "status": "error",
                "version": "unknown",
                "message": f"Tool found but returned error: {result.stderr[-300:]}"
            }

    except FileNotFoundError:
        return {
            "status": "not_found",
            "version": "not_installed",
            "message": "pdf2zh-next is not installed. Install with: pip install pdf2zh-next"
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "version": "unknown",
            "message": "Tool check timed out."
        }
    except Exception as e:
        return {
            "status": "error",
            "version": "unknown",
            "message": f"Error checking tool: {e}"
        }

def main():
    """Main entry point for the console script."""
    print("Starting Huoshui PDF Translator MCP server (SSE mode)...")
    # SSE 传输，监听所有网卡，供局域网内 RikkaHub 等移动端连接
    mcp.run(transport="sse", host="0.0.0.0", port=8000)

# Main execution
if __name__ == "__main__":
    main()
