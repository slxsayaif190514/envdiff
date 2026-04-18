import pytest
from envdiff.promoter import promote_keys, PromoteResult, PromoteEntry


@pytest.fixture
def source():
    return {"DB_HOST": "prod-db", "API_KEY": "secret", "PORT": "5432"}


@pytest.fixture
def target():
    return {"DB_HOST": "dev-db", "PORT": "3000"}


def test_promote_single_key(source, target):
    result = promote_keys(source, target, ["API_KEY"])
    assert result.promote_count == 1
    assert result.promoted[0].key == "API_KEY"
    assert result.promoted[0].value == "secret"


def test_promote_missing_key_is_skipped(source, target):
    result = promote_keys(source, target, ["MISSING_KEY"])
    assert result.promote_count == 0
    assert "MISSING_KEY" in result.skipped


def test_promote_overwrite_existing(source, target):
    result = promote_keys(source, target, ["DB_HOST"])
    assert result.promote_count == 1
    entry = result.promoted[0]
    assert entry.key == "DB_HOST"
    assert entry.value == "prod-db"
    assert entry.overwritten_value == "dev-db"


def test_promote_no_overwrite_skips_existing(source, target):
    result = promote_keys(source, target, ["DB_HOST"], overwrite=False)
    assert result.promote_count == 0
    assert "DB_HOST" in result.skipped


def test_promote_no_overwrite_allows_new_key(source, target):
    result = promote_keys(source, target, ["API_KEY"], overwrite=False)
    assert result.promote_count == 1


def test_promote_multiple_keys_sorted(source, target):
    result = promote_keys(source, target, ["PORT", "API_KEY", "DB_HOST"])
    keys = [e.key for e in result.promoted]
    assert keys == sorted(keys)


def test_promote_result_source_target_names(source, target):
    result = promote_keys(source, target, [], source_name="prod", target_name="staging")
    assert result.source == "prod"
    assert result.target == "staging"


def test_promote_is_empty_when_nothing_promoted(source, target):
    result = promote_keys(source, target, [])
    assert result.is_empty


def test_no_overwritten_value_when_key_is_new(source, target):
    result = promote_keys(source, target, ["API_KEY"])
    assert result.promoted[0].overwritten_value is None


def test_same_value_not_marked_as_overwritten():
    src = {"KEY": "value"}
    tgt = {"KEY": "value"}
    result = promote_keys(src, tgt, ["KEY"])
    assert result.promoted[0].overwritten_value is None
