"""Pydantic models for Text Utils MCP Server responses."""

import re

from pydantic import BaseModel, Field


class ReverseTextResponse(BaseModel):
    """Response model for reverse_text tool."""

    original: str = Field(..., description="The original text")
    reversed: str = Field(..., description="The reversed text")
    length: int = Field(..., description="Length of the text")


class TextInfoResponse(BaseModel):
    """Response model for text_info tool."""

    text: str = Field(..., description="The input text")
    length: int = Field(..., description="Total character count")
    word_count: int = Field(..., description="Number of words")
    char_count_no_spaces: int = Field(..., description="Characters excluding spaces")
    uppercase_count: int = Field(..., description="Number of uppercase letters")
    lowercase_count: int = Field(..., description="Number of lowercase letters")
    digit_count: int = Field(..., description="Number of digits")
    line_count: int = Field(..., description="Number of lines")


class TransformCaseResponse(BaseModel):
    """Response model for transform_case tool."""

    original: str = Field(..., description="The original text")
    transformed: str = Field(..., description="The transformed text")
    from_format: str = Field(..., description="Detected input format")
    to_format: str = Field(..., description="Target output format")


class SlugifyResponse(BaseModel):
    """Response model for slugify tool."""

    original: str = Field(..., description="The original text")
    slug: str = Field(..., description="URL-safe slug")


class ExtractUrlsResponse(BaseModel):
    """Response model for extract_urls tool."""

    text: str = Field(..., description="The input text")
    urls: list[str] = Field(..., description="Extracted URLs")
    count: int = Field(..., description="Number of URLs found")


class TruncateResponse(BaseModel):
    """Response model for truncate tool."""

    original: str = Field(..., description="The original text")
    truncated: str = Field(..., description="The truncated text")
    original_length: int = Field(..., description="Original character count")
    truncated_length: int = Field(..., description="Truncated character count")
    was_truncated: bool = Field(..., description="Whether truncation occurred")


class CountTokensResponse(BaseModel):
    """Response model for count_tokens tool."""

    text: str = Field(..., description="The input text")
    estimated_tokens: int = Field(..., description="Estimated token count")
    word_count: int = Field(..., description="Word count")
    char_count: int = Field(..., description="Character count")
    method: str = Field(default="words * 1.3", description="Estimation method used")


# Helpers for case detection/transformation

_CASE_FORMATS = {
    "snake_case": re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)+$"),
    "SCREAMING_SNAKE_CASE": re.compile(r"^[A-Z][A-Z0-9]*(_[A-Z0-9]+)+$"),
    "camelCase": re.compile(r"^[a-z][a-zA-Z0-9]*$"),
    "PascalCase": re.compile(r"^[A-Z][a-zA-Z0-9]*$"),
    "kebab-case": re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)+$"),
    "Title Case": re.compile(r"^[A-Z][a-z]+(?: [A-Z][a-z]+)+$"),
}


def detect_case(text: str) -> str:
    """Detect the case format of a string."""
    for name, pattern in _CASE_FORMATS.items():
        if pattern.match(text):
            return name
    return "unknown"


def split_words(text: str) -> list[str]:
    """Split text into words regardless of input format."""
    # Handle camelCase / PascalCase
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", text)
    # Handle sequences of uppercase followed by lowercase
    text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", text)
    # Split on non-alphanumeric
    return [w.lower() for w in re.split(r"[^a-zA-Z0-9]+", text) if w]


def to_case(words: list[str], target: str) -> str:
    """Convert word list to target case format."""
    match target:
        case "snake_case":
            return "_".join(words)
        case "SCREAMING_SNAKE_CASE":
            return "_".join(w.upper() for w in words)
        case "camelCase":
            return words[0] + "".join(w.capitalize() for w in words[1:])
        case "PascalCase":
            return "".join(w.capitalize() for w in words)
        case "kebab-case":
            return "-".join(words)
        case "Title Case":
            return " ".join(w.capitalize() for w in words)
        case _:
            return "_".join(words)
