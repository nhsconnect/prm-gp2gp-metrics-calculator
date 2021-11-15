import pytest

from prmcalculator.pipeline.config import EnvConfig, InvalidEnvironmentVariableValue


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


def test_read_optional_int_returns_one_given_string_value_one():
    env = EnvConfig({"OPTIONAL_INT_CONFIG": "1"})
    actual = env.read_optional_int(name="OPTIONAL_INT_CONFIG", default=0)
    expected = 1

    assert actual == expected


def test_read_optional_int_throws_exception_given_invalid_string():
    env = EnvConfig({"OPTIONAL_INT_CONFIG": "one"})

    with pytest.raises(InvalidEnvironmentVariableValue) as e:
        env.read_optional_int(name="OPTIONAL_INT_CONFIG", default=0)
        assert (
            str(e)
            == "Expected environment variable OPTIONAL_INT_CONFIG value is invalid, exiting..."
        )
