# MCP Reverse Text Service

A Model Context Protocol (MCP) service that provides text manipulation tools including text reversal and analysis.

## Features

- **reverse_text**: Reverse the characters in a text string
- **text_info**: Get detailed information about a text string (length, word count, character analysis)

## Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/NimbleBrainInc/mcp-reverse-text.git
cd mcp-reverse-text

# Install dependencies with uv
uv sync

# Run the server
uv run python server.py

# Or install in editable mode
uv pip install -e .
python server.py
```

The server will start on `http://localhost:8000` with:
- Health check: `GET /health`
- Service discovery: `GET /mcp/discover`
- MCP endpoint: `POST /mcp`

### Docker

```bash
# Build the image
docker build -t nimblebrain/mcp-reverse-text .

# Run the container
docker run -p 8000:8000 nimblebrain/mcp-reverse-text
```

## Configuration

The service metadata is defined in `mcp.json`:

```json
{
  "name": "reverse-text",
  "description": "Text manipulation service with reverse and analysis tools",
  "version": "1.0.0",
  "category": "text-processing",
  "port": 8000,
  "healthPath": "/health"
}
```

This file provides basic service information that can be used by any MCP platform or deployment system.

## API Usage

### Reverse Text

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "reverse_text",
      "arguments": {"text": "Hello World"}
    },
    "id": 1
  }'
```

### Text Analysis

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "text_info",
      "arguments": {"text": "Hello World"}
    },
    "id": 1
  }'
```

## Development

### Testing

```bash
# Install with dev dependencies
uv sync --group dev

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=server

# Run tests in development mode
uv run --group dev pytest -v
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.