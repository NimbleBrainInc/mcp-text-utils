# MCP Text Utils

A text manipulation toolkit for the Model Context Protocol (MCP). Provides 7 tools for common text operations.

## Tools

| Tool | Description |
|------|-------------|
| `reverse_text` | Reverse the characters in a text string |
| `text_info` | Analyze text: word count, character breakdown, line count |
| `transform_case` | Convert between snake_case, camelCase, kebab-case, PascalCase, SCREAMING_SNAKE_CASE, Title Case |
| `slugify` | Convert text into a URL-safe slug |
| `extract_urls` | Extract all URLs from a block of text |
| `truncate` | Truncate text at word boundaries with configurable suffix |
| `count_tokens` | Estimate LLM token count (word-based heuristic) |

## Install via mpak

```bash
mpak install @nimblebraininc/text-utils
```

## Local Development

```bash
uv sync
make test        # Run tests
make check       # Format + lint + typecheck + tests
make run         # Run server (stdio)
make run-http    # Run HTTP server
make bundle      # Build MCPB bundle
```

## Claude Desktop Config

```json
{
  "mcpServers": {
    "text-utils": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/mcp-text-utils", "python", "-m", "mcp_text_utils.server"]
    }
  }
}
```

## License

MIT
