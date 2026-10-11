"""Parse and validate the raw LLM output. Pure functions, no I/O."""

import json
import re

_CODE_FENCE = re.compile(r"^```[a-zA-Z]*\s*(.*?)\s*```$", re.DOTALL)
# Whitespace plus the unicode hyphens, dashes and minus signs.
_SEPARATORS = re.compile(r"[\s‐-―−﹘﹣－]+")
_NOT_KEBAB = re.compile(r"[^a-z0-9-]")
_REPEATED_HYPHENS = re.compile(r"-{2,}")


class LLMOutputError(ValueError):
    """The LLM response was not the JSON object we asked for."""


def _strip_code_fences(raw: str) -> str:
    text = raw.strip()
    match = _CODE_FENCE.match(text)
    return match.group(1) if match else text


def _normalize_tag(tag: str) -> str:
    """'Credit‑Bureau API' -> 'credit-bureau-api'. Raises if nothing is left."""
    tag = _SEPARATORS.sub("-", tag.lower())
    tag = _NOT_KEBAB.sub("", tag)
    tag = _REPEATED_HYPHENS.sub("-", tag).strip("-")
    if not tag:
        raise LLMOutputError("A tag is empty after normalization")
    return tag


def parse_llm_output(raw: str) -> tuple[str, list[str]]:
    """Return (summary, tags) or raise LLMOutputError."""
    try:
        data = json.loads(_strip_code_fences(raw))
    except json.JSONDecodeError as e:
        raise LLMOutputError(f"Output is not valid JSON: {e}") from e

    if not isinstance(data, dict):
        raise LLMOutputError("Output is not a JSON object")

    summary = data.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        raise LLMOutputError("'summary' must be a non-empty string")

    tags = data.get("tags")
    if not isinstance(tags, list) or len(tags) != 3:
        raise LLMOutputError("'tags' must be a list of exactly 3 items")
    if not all(isinstance(tag, str) and tag.strip() for tag in tags):
        raise LLMOutputError("Every tag must be a non-empty string")

    normalized = [_normalize_tag(tag) for tag in tags]
    if len(set(normalized)) != len(normalized):
        raise LLMOutputError("Tags must be unique after normalization")

    return summary.strip(), normalized
