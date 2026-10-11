import pytest

from app.parser import LLMOutputError, parse_llm_output


def test_valid_json():
    raw = '{"summary": "A short summary.", "tags": ["python", "web-apis", "testing"]}'
    assert parse_llm_output(raw) == ("A short summary.", ["python", "web-apis", "testing"])


def test_json_in_code_fences():
    raw = '```json\n{"summary": "Fenced.", "tags": ["a", "b", "c"]}\n```'
    assert parse_llm_output(raw) == ("Fenced.", ["a", "b", "c"])


def test_tags_are_normalized():
    # U+2011 is a non-breaking hyphen.
    raw = '{"summary": "S.", "tags": ["Credit‑Bureau API", " Machine  Learning ", "--data!--"]}'
    _, tags = parse_llm_output(raw)
    assert tags == ["credit-bureau-api", "machine-learning", "data"]


@pytest.mark.parametrize(
    "raw",
    [
        pytest.param("not json at all", id="invalid-json"),
        pytest.param("", id="empty-string"),
        pytest.param('{"tags": ["a", "b", "c"]}', id="missing-summary"),
        pytest.param('{"summary": "  ", "tags": ["a", "b", "c"]}', id="empty-summary"),
        pytest.param('{"summary": "S.", "tags": ["a", "b"]}', id="two-tags"),
        pytest.param('{"summary": "S.", "tags": ["a", "b", "c", "d"]}', id="four-tags"),
        pytest.param('{"summary": "S.", "tags": ["a", "b", 3]}', id="non-string-tag"),
        pytest.param('{"summary": "S.", "tags": ["a", "b", "!!!"]}', id="tag-empty-after-normalizing"),
    ],
)
def test_rejects_bad_output(raw):
    with pytest.raises(LLMOutputError):
        parse_llm_output(raw)
