"""Tests for Text Utils MCP server."""

import pytest
from fastmcp import Client

from mcp_text_utils.server import mcp


@pytest.fixture
def mcp_server():
    """Return the MCP server instance."""
    return mcp


@pytest.mark.asyncio
async def test_reverse_text(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("reverse_text", {"text": "Hello World"})
        data = result.data
        assert data.original == "Hello World"
        assert data.reversed == "dlroW olleH"
        assert data.length == 11


@pytest.mark.asyncio
async def test_text_info(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("text_info", {"text": "Hello World 123"})
        data = result.data
        assert data.length == 15
        assert data.word_count == 3
        assert data.char_count_no_spaces == 13
        assert data.uppercase_count == 2
        assert data.lowercase_count == 8
        assert data.digit_count == 3
        assert data.line_count == 1


@pytest.mark.asyncio
async def test_text_info_multiline(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("text_info", {"text": "line1\nline2\nline3"})
        assert result.data.line_count == 3


@pytest.mark.asyncio
async def test_transform_case_snake_to_camel(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "transform_case", {"text": "hello_world_test", "target": "camelCase"}
        )
        data = result.data
        assert data.transformed == "helloWorldTest"
        assert data.from_format == "snake_case"
        assert data.to_format == "camelCase"


@pytest.mark.asyncio
async def test_transform_case_camel_to_snake(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "transform_case", {"text": "helloWorldTest", "target": "snake_case"}
        )
        assert result.data.transformed == "hello_world_test"


@pytest.mark.asyncio
async def test_transform_case_to_kebab(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "transform_case", {"text": "HelloWorld", "target": "kebab-case"}
        )
        assert result.data.transformed == "hello-world"


@pytest.mark.asyncio
async def test_transform_case_to_screaming(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "transform_case", {"text": "hello_world", "target": "SCREAMING_SNAKE_CASE"}
        )
        assert result.data.transformed == "HELLO_WORLD"


@pytest.mark.asyncio
async def test_transform_case_to_pascal(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "transform_case", {"text": "hello-world", "target": "PascalCase"}
        )
        assert result.data.transformed == "HelloWorld"


@pytest.mark.asyncio
async def test_transform_case_to_title(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "transform_case", {"text": "hello_world", "target": "Title Case"}
        )
        assert result.data.transformed == "Hello World"


@pytest.mark.asyncio
async def test_transform_case_invalid_target(mcp_server):
    async with Client(mcp_server) as client:
        with pytest.raises(Exception, match="Unknown target case"):
            await client.call_tool("transform_case", {"text": "hello", "target": "invalid_case"})


@pytest.mark.asyncio
async def test_slugify(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("slugify", {"text": "Hello World! This is a Test"})
        assert result.data.slug == "hello-world-this-is-a-test"


@pytest.mark.asyncio
async def test_slugify_unicode(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("slugify", {"text": "Caf\u00e9 & R\u00e9sum\u00e9"})
        assert result.data.slug == "cafe-resume"


@pytest.mark.asyncio
async def test_extract_urls(mcp_server):
    async with Client(mcp_server) as client:
        text = "Visit https://example.com and http://test.org/path?q=1 for more"
        result = await client.call_tool("extract_urls", {"text": text})
        content = result.structured_content
        assert content["count"] == 2
        assert "https://example.com" in content["urls"]
        assert "http://test.org/path?q=1" in content["urls"]


@pytest.mark.asyncio
async def test_extract_urls_none(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("extract_urls", {"text": "no urls here"})
        content = result.structured_content
        assert content["count"] == 0
        assert content["urls"] == []


@pytest.mark.asyncio
async def test_truncate_short_text(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("truncate", {"text": "short", "max_length": 100})
        data = result.data
        assert data.truncated == "short"
        assert data.was_truncated is False


@pytest.mark.asyncio
async def test_truncate_long_text(mcp_server):
    async with Client(mcp_server) as client:
        text = "This is a longer sentence that should be truncated at a word boundary"
        result = await client.call_tool("truncate", {"text": text, "max_length": 30})
        data = result.data
        assert data.was_truncated is True
        assert data.truncated_length <= 30
        assert data.truncated.endswith("...")


@pytest.mark.asyncio
async def test_truncate_custom_suffix(mcp_server):
    async with Client(mcp_server) as client:
        text = "This is a longer sentence that should be truncated"
        result = await client.call_tool(
            "truncate", {"text": text, "max_length": 25, "suffix": " [more]"}
        )
        assert result.data.truncated.endswith("[more]")


@pytest.mark.asyncio
async def test_count_tokens(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("count_tokens", {"text": "Hello world this is a test"})
        data = result.data
        assert data.word_count == 6
        assert data.char_count == 26
        assert data.estimated_tokens >= data.word_count


@pytest.mark.asyncio
async def test_tools_list(mcp_server):
    async with Client(mcp_server) as client:
        tools = await client.list_tools()
        tool_names = {tool.name for tool in tools}
        expected = {
            "reverse_text",
            "text_info",
            "transform_case",
            "slugify",
            "extract_urls",
            "truncate",
            "count_tokens",
        }
        assert expected == tool_names
