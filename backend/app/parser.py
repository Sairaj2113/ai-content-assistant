"""Parse and validate the raw LLM output. Pure functions, no I/O."""

import json
import re

_CODE_FENCE = re.compile(r"^```[a-zA-Z]*\s*(.*?)\s*```$", re.DOTALL)


class LLMOutputError(ValueError):
    """The LLM response was not the JSON object we asked for."""


def _strip_code_fences(raw: str) -> str:
    text = raw.strip()
    match = _CODE_FENCE.match(text)
    return match.group(1) if match else text


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

    return summary.strip(), [tag.strip().lower() for tag in tags]
