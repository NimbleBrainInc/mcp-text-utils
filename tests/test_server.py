#!/usr/bin/env python3
"""Tests for reverse text MCP server"""

import json
import sys
from pathlib import Path

import pytest
from fastmcp import Client

# Add parent directory to path for server import
sys.path.insert(0, str(Path(__file__).parent.parent))
from server import mcp  # noqa: E402


@pytest.fixture
def mcp_server():
    """Return the MCP server instance"""
    return mcp


@pytest.mark.asyncio
async def test_reverse_text_tool(mcp_server):
    """Test reverse_text tool functionality"""
    async with Client(mcp_server) as client:
        result = await client.call_tool("reverse_text", {"text": "Hello World"})

        # Parse the JSON result
        result_data = json.loads(result.data)
        assert result_data["original_text"] == "Hello World"
        assert result_data["reversed_text"] == "dlroW olleH"
        assert result_data["length"] == 11
        assert "timestamp" in result_data


@pytest.mark.asyncio
async def test_text_info_tool(mcp_server):
    """Test text_info tool functionality"""
    async with Client(mcp_server) as client:
        result = await client.call_tool("text_info", {"text": "Hello World 123"})

        # Parse the JSON result
        result_data = json.loads(result.data)
        assert result_data["text"] == "Hello World 123"
        assert result_data["length"] == 15
        assert result_data["word_count"] == 3
        assert result_data["character_count"] == 15
        assert result_data["character_count_no_spaces"] == 13
        assert result_data["uppercase_count"] == 2  # H, W
        assert result_data["lowercase_count"] == 8
        assert result_data["digit_count"] == 3
        assert "timestamp" in result_data


@pytest.mark.asyncio
async def test_tools_list(mcp_server):
    """Test that tools are properly registered"""
    async with Client(mcp_server) as client:
        tools = await client.list_tools()

        assert len(tools) == 2
        tool_names = [tool.name for tool in tools]
        assert "reverse_text" in tool_names
        assert "text_info" in tool_names

        # Check tool descriptions
        reverse_tool = next(t for t in tools if t.name == "reverse_text")
        assert "Reverse the characters in a text string" in reverse_tool.description

        text_info_tool = next(t for t in tools if t.name == "text_info")
        assert "Get information about a text string" in text_info_tool.description


@pytest.mark.asyncio
async def test_invalid_tool(mcp_server):
    """Test calling invalid tool"""
    async with Client(mcp_server) as client:
        try:
            await client.call_tool("invalid_tool", {})
            assert False, "Should have raised an exception"
        except Exception as e:
            # Should raise an exception for invalid tool
            assert "invalid_tool" in str(e).lower() or "not found" in str(e).lower()
