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
