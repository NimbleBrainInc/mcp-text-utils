"""Text Utils MCP Server - A text manipulation toolkit."""

import math
import re
import unicodedata

from fastmcp import FastMCP

from .api_models import (
    CountTokensResponse,
    ExtractUrlsResponse,
    ReverseTextResponse,
    SlugifyResponse,
    TextInfoResponse,
    TransformCaseResponse,
    TruncateResponse,
    detect_case,
    split_words,
    to_case,
)

mcp = FastMCP("Text Utils MCP Server")

_URL_PATTERN = re.compile(
    r"https?://[^\s<>\"')\]]+",
    re.IGNORECASE,
)

_VALID_CASES = [
    "snake_case",
    "SCREAMING_SNAKE_CASE",
    "camelCase",
    "PascalCase",
    "kebab-case",
    "Title Case",
]


@mcp.tool
def reverse_text(text: str) -> ReverseTextResponse:
    """Reverse the characters in a text string."""
    return ReverseTextResponse(
        original=text,
        reversed=text[::-1],
        length=len(text),
    )


@mcp.tool
def text_info(text: str) -> TextInfoResponse:
    """Analyze a text string: word count, character breakdown, line count."""
    return TextInfoResponse(
        text=text,
        length=len(text),
        word_count=len(text.split()),
        char_count_no_spaces=len(text.replace(" ", "")),
        uppercase_count=sum(1 for c in text if c.isupper()),
        lowercase_count=sum(1 for c in text if c.islower()),
        digit_count=sum(1 for c in text if c.isdigit()),
        line_count=text.count("\n") + 1,
    )


@mcp.tool
def transform_case(text: str, target: str) -> TransformCaseResponse:
    """Convert text between case formats.

    Supported targets: snake_case, SCREAMING_SNAKE_CASE, camelCase,
    PascalCase, kebab-case, Title Case.
    """
    if target not in _VALID_CASES:
        msg = f"Unknown target case '{target}'. Valid: {', '.join(_VALID_CASES)}"
        raise ValueError(msg)

    detected = detect_case(text)
    words = split_words(text)
    transformed = to_case(words, target)

    return TransformCaseResponse(
        original=text,
        transformed=transformed,
        from_format=detected,
        to_format=target,
    )


@mcp.tool
def slugify(text: str) -> SlugifyResponse:
    """Convert text into a URL-safe slug."""
    slug = unicodedata.normalize("NFKD", text)
    slug = slug.encode("ascii", "ignore").decode("ascii")
    slug = slug.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")

    return SlugifyResponse(original=text, slug=slug)


@mcp.tool
def extract_urls(text: str) -> ExtractUrlsResponse:
    """Extract all URLs from a block of text."""
    urls = _URL_PATTERN.findall(text)
    return ExtractUrlsResponse(text=text, urls=urls, count=len(urls))


@mcp.tool
def truncate(text: str, max_length: int = 100, suffix: str = "...") -> TruncateResponse:
    """Truncate text at a word boundary with a configurable suffix."""
    if len(text) <= max_length:
        return TruncateResponse(
            original=text,
            truncated=text,
            original_length=len(text),
            truncated_length=len(text),
            was_truncated=False,
        )

    limit = max_length - len(suffix)
    if limit <= 0:
        truncated = suffix[:max_length]
    else:
        truncated = text[:limit]
        last_space = truncated.rfind(" ")
        if last_space > 0:
            truncated = truncated[:last_space]
        truncated = truncated.rstrip() + suffix

    return TruncateResponse(
        original=text,
        truncated=truncated,
        original_length=len(text),
        truncated_length=len(truncated),
        was_truncated=True,
    )


@mcp.tool
def count_tokens(text: str) -> CountTokensResponse:
    """Estimate the token count for a text string.

    Uses a word-based heuristic (words * 1.3) which approximates
    most LLM tokenizers. Useful for checking if text fits within
    context windows.
    """
    words = text.split()
    word_count = len(words)
    estimated = math.ceil(word_count * 1.3)

    return CountTokensResponse(
        text=text,
        estimated_tokens=estimated,
        word_count=word_count,
        char_count=len(text),
    )


# ASGI entrypoint (nimbletools-core container deployment)
app = mcp.http_app()

# Stdio entrypoint (mpak / Claude Desktop)
if __name__ == "__main__":
    mcp.run()
