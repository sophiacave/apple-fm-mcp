"""
Apple Foundation Models MCP Server

Exposes Apple's on-device 3B parameter LLM to Claude Code and Claude Desktop
via the Model Context Protocol. Zero API cost, fully private, runs on Neural Engine.

Requirements: macOS 26+, Apple Silicon, Apple Intelligence enabled
"""

import asyncio
import json
import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

logger = logging.getLogger(__name__)

# Lazy import — only loads on macOS 26+
_fm = None

def _get_fm():
    global _fm
    if _fm is None:
        try:
            import apple_fm_sdk as fm
            model = fm.SystemLanguageModel()
            available, reason = model.is_available()
            if not available:
                raise RuntimeError(f"Apple Foundation Models not available: {reason}")
            _fm = fm
        except ImportError:
            raise RuntimeError(
                "apple-fm-sdk not installed. Run: pip install apple-fm-sdk\n"
                "Requires macOS 26+ with Apple Intelligence enabled."
            )
    return _fm


app = Server("apple-fm-mcp")


@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="fm_generate",
            description=(
                "Generate text using Apple's on-device Foundation Model. "
                "Fast (~1s), free, private. Best for short generations, "
                "summaries, classifications, and quick answers. "
                "4096 token context limit."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The prompt to send to the on-device model",
                    },
                },
                "required": ["prompt"],
            },
        ),
        Tool(
            name="fm_summarize",
            description=(
                "Summarize text into bullet points using Apple's on-device model. "
                "Returns structured output with key points and a takeaway. "
                "Best for lesson content, articles, and documentation."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The text content to summarize (max ~3000 chars)",
                    },
                },
                "required": ["content"],
            },
        ),
        Tool(
            name="fm_classify",
            description=(
                "Classify text into categories using Apple's on-device model. "
                "Provide the text and a list of possible categories. "
                "Returns the best matching category with confidence."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to classify",
                    },
                    "categories": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of possible categories",
                    },
                },
                "required": ["text", "categories"],
            },
        ),
        Tool(
            name="fm_extract",
            description=(
                "Extract structured data from text using Apple's on-device model. "
                "Provide the text and a description of what to extract. "
                "Returns extracted entities as JSON."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to extract data from",
                    },
                    "extract": {
                        "type": "string",
                        "description": "Description of what to extract (e.g., 'names and dates', 'action items', 'technical terms')",
                    },
                },
                "required": ["text", "extract"],
            },
        ),
        Tool(
            name="fm_status",
            description="Check if Apple Foundation Models are available on this device.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "fm_status":
        return await _handle_status()
    elif name == "fm_generate":
        return await _handle_generate(arguments)
    elif name == "fm_summarize":
        return await _handle_summarize(arguments)
    elif name == "fm_classify":
        return await _handle_classify(arguments)
    elif name == "fm_extract":
        return await _handle_extract(arguments)
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def _handle_status():
    try:
        fm = _get_fm()
        return [TextContent(type="text", text=(
            "Apple Foundation Models: AVAILABLE\n"
            "Model: ~3B parameters, on-device\n"
            "Engine: Apple Neural Engine\n"
            "Context: 4096 tokens\n"
            "Cost: $0 (on-device inference)\n"
            "Privacy: Full (no data leaves device)"
        ))]
    except Exception as e:
        return [TextContent(type="text", text=f"Apple Foundation Models: UNAVAILABLE\nReason: {e}")]


async def _handle_generate(arguments: dict):
    fm = _get_fm()
    prompt = arguments.get("prompt", "")
    if not prompt:
        return [TextContent(type="text", text="Error: prompt is required")]

    session = fm.LanguageModelSession()
    response = await session.respond(prompt)
    return [TextContent(type="text", text=str(response))]


async def _handle_summarize(arguments: dict):
    fm = _get_fm()
    content = arguments.get("content", "")
    if not content:
        return [TextContent(type="text", text="Error: content is required")]

    prompt = (
        "Summarize the following text in 3-5 concise bullet points. "
        "Focus on the most important concepts. End with a single key takeaway.\n\n"
        f"Text:\n{content[:3000]}"
    )

    session = fm.LanguageModelSession()
    response = await session.respond(prompt)
    return [TextContent(type="text", text=str(response))]


async def _handle_classify(arguments: dict):
    fm = _get_fm()
    text = arguments.get("text", "")
    categories = arguments.get("categories", [])
    if not text or not categories:
        return [TextContent(type="text", text="Error: text and categories are required")]

    cats = ", ".join(categories)
    prompt = (
        f"Classify the following text into exactly ONE of these categories: {cats}\n\n"
        f"Text: {text[:2000]}\n\n"
        "Respond with just the category name, then a brief explanation of why."
    )

    session = fm.LanguageModelSession()
    response = await session.respond(prompt)
    return [TextContent(type="text", text=str(response))]


async def _handle_extract(arguments: dict):
    fm = _get_fm()
    text = arguments.get("text", "")
    extract = arguments.get("extract", "")
    if not text or not extract:
        return [TextContent(type="text", text="Error: text and extract are required")]

    prompt = (
        f"Extract the following from the text: {extract}\n\n"
        f"Text: {text[:2000]}\n\n"
        "Return the extracted information as a structured list."
    )

    session = fm.LanguageModelSession()
    response = await session.respond(prompt)
    return [TextContent(type="text", text=str(response))]


def main():
    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())

    asyncio.run(run())


if __name__ == "__main__":
    main()
