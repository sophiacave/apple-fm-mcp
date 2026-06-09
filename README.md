# Apple Foundation Models MCP Server

Expose Apple's on-device 3B parameter LLM to Claude Code and Claude Desktop via MCP. Zero API cost, fully private, runs on Neural Engine.

## Requirements

- macOS 26+ (Tahoe or later)
- Apple Silicon (M1/M2/M3/M4)
- Apple Intelligence enabled in System Settings
- Python 3.10+

## Install

```bash
pip install apple-fm-mcp
```

## Configure

Add to your Claude Code config (`~/.claude/mcp.json`):

```json
{
  "mcpServers": {
    "apple-fm": {
      "command": "apple-fm-mcp"
    }
  }
}
```

Or Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "apple-fm": {
      "command": "apple-fm-mcp"
    }
  }
}
```

## Tools

| Tool | Description | Latency |
|------|-------------|---------|
| `fm_generate` | Free-form text generation | ~1s |
| `fm_summarize` | Summarize text into bullet points | ~4s |
| `fm_classify` | Classify text into categories | ~2s |
| `fm_extract` | Extract structured data from text | ~3s |
| `fm_status` | Check model availability | instant |

## Why Use This?

- **Free**: No API keys, no tokens, no cloud costs
- **Private**: All inference on-device, no data leaves your Mac
- **Fast**: Neural Engine optimized, ~1s for generation
- **Complementary**: Use alongside Claude for tasks where on-device speed matters

## When to Use Apple FM vs Claude

| Task | Use Apple FM | Use Claude |
|------|-------------|-----------|
| Quick classification | Yes | Overkill |
| Text summarization | Yes (short text) | Yes (long documents) |
| Code generation | No | Yes |
| Complex reasoning | No | Yes |
| Data extraction | Yes (simple) | Yes (complex) |
| Privacy-critical | Yes | Depends |

## Built by [Like One](https://likeone.ai)

AI education from a 501(c)(3) nonprofit. 50+ free courses on Claude, MCP, agents, and AI architecture.

## License

MIT
