import pytest

from prmcalculator.pipeline.config import EnvConfig


@pytest.mark.parametrize(
    "string",
    ["True", "true", "TRUE", "TrUe"],
)
def test_read_optional_bool_returns_true_given_different_casing(string):
    env = EnvConfig({"OPTIONAL_BOOL_CONFIG": string})
    actual = env.read_optional_bool(name="OPTIONAL_BOOL_CONFIG", default=False)
    expected = True

    assert actual == expected


@pytest.mark.parametrize(
    "string",
    ["False", "false", "FALSE", "FaLse", "mango"],
)
def test_read_optional_bool_returns_false_given_different_casing(string):
    env = EnvConfig({"OPTIONAL_BOOL_CONFIG": string})
    actual = env.read_optional_bool(name="OPTIONAL_BOOL_CONFIG", default=True)
    expected = False

    assert actual == expected


@pytest.mark.parametrize(
    "string",
    ["1"],
)
def test_read_optional_int_returns_one_given_string_value_one(string):
    env = EnvConfig({"OPTIONAL_INT_CONFIG": string})
    actual = env.read_optional_int(name="OPTIONAL_INT_CONFIG", default=0)
    expected = 1

    assert actual == expected


def test_read_optional_int_returns_default_value_given_invalid_string():
    env = EnvConfig({"OPTIONAL_INT_CONFIG": ""})
    actual = env.read_optional_int(name="OPTIONAL_INT_CONFIG", default=0)
    expected = 0

    assert actual == expected
