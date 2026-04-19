import pytest
from envdiff.flattener import FlatEntry, FlattenResult, flatten_env, _split_key


@pytest.fixture
def sample_env():
    return {
        "DB__HOST": "localhost",
        "DB__PORT": "5432",
        "APP_NAME": "myapp",
        "AUTH__JWT__SECRET": "topsecret",
    }


def test_flatten_returns_result(sample_env):
    result = flatten_env(sample_env, filename="prod.env")
    assert isinstance(result, FlattenResult)


def test_filename_stored(sample_env):
    result = flatten_env(sample_env, filename="prod.env")
    assert result.filename == "prod.env"


def test_key_count_matches_env(sample_env):
    result = flatten_env(sample_env)
    assert result.key_count == len(sample_env)


def test_nested_count_only_double_underscore(sample_env):
    result = flatten_env(sample_env, separator="__")
    # DB__HOST, DB__PORT, AUTH__JWT__SECRET are nested; APP_NAME is not
    assert result.nested_count == 3


def test_flat_key_has_single_path_segment():
    result = flatten_env({"APP_NAME": "myapp"})
    entry = result.entries[0]
    assert entry.nested_path == ["APP_NAME"]


def test_nested_key_splits_correctly():
    result = flatten_env({"DB__HOST": "localhost"}, separator="__")
    entry = result.entries[0]
    assert entry.nested_path == ["DB", "HOST"]


def test_deeply_nested_key():
    result = flatten_env({"AUTH__JWT__SECRET": "x"}, separator="__")
    entry = result.entries[0]
    assert entry.nested_path == ["AUTH", "JWT", "SECRET"]


def test_as_dict_returns_original_keys(sample_env):
    result = flatten_env(sample_env)
    assert result.as_dict() == sample_env


def test_entry_source_matches_filename():
    result = flatten_env({"KEY": "val"}, filename="staging.env")
    assert result.entries[0].source == "staging.env"


def test_split_key_no_separator():
    assert _split_key("SIMPLE", "__") == ["SIMPLE"]


def test_split_key_with_separator():
    assert _split_key("A__B__C", "__") == ["A", "B", "C"]


def test_custom_separator():
    result = flatten_env({"DB.HOST": "localhost"}, separator=".")
    entry = result.entries[0]
    assert entry.nested_path == ["DB", "HOST"]


def test_repr_flat_entry():
    e = FlatEntry(key="A", value="1", source="f.env", nested_path=["A"])
    assert "A=" in repr(e)


def test_empty_env():
    result = flatten_env({})
    assert result.key_count == 0
    assert result.nested_count == 0
