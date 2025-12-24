#!/usr/bin/env python3
"""
Reverse Text MCP Server - FastMCP Implementation
"""

import json
from datetime import UTC, datetime

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

# Create FastMCP server
mcp = FastMCP("Reverse Text MCP Server")


@mcp.tool
def reverse_text(text: str) -> str:
    """Reverse the characters in a text string"""
    result = {
        "original_text": text,
        "reversed_text": text[::-1],
        "length": len(text),
        "timestamp": datetime.now(UTC).isoformat(),
    }
    return json.dumps(result, indent=2)


@mcp.tool
def text_info(text: str) -> str:
    """Get information about a text string"""
    info = {
        "text": text,
        "length": len(text),
        "word_count": len(text.split()),
        "character_count": len(text),
        "character_count_no_spaces": len(text.replace(" ", "")),
        "uppercase_count": sum(1 for c in text if c.isupper()),
        "lowercase_count": sum(1 for c in text if c.islower()),
        "digit_count": sum(1 for c in text if c.isdigit()),
        "timestamp": datetime.now(UTC).isoformat(),
    }
    return json.dumps(info, indent=2)


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    return JSONResponse({"status": "healthy"})


# Create ASGI application for uvicorn
app = mcp.http_app()
