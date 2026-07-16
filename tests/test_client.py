import pytest

from ckan_client.client import check_kwargs


@pytest.mark.parametrize(
    "given, expected, raised",
    [
        (
            None,
            {
                "a": {
                    "type": "int",
                    "description": "Description",
                    "optional": True,
                }
            },
            False,
        ),
        (
            {"a": 1},
            {
                "a": {
                    "type": "int",
                    "description": "Description",
                    "optional": True,
                }
            },
            False,
        ),
        (
            {"b": 1},
            {
                "a": {
                    "type": "int",
                    "description": "Description",
                    "optional": True,
                }
            },
            True,
        ),
    ],
)
def test_check_kwargs(given, expected, raised):
    if raised:
        with pytest.raises(ValueError):
            check_kwargs(given, expected)
    else:
        assert check_kwargs(given, expected) is None


def test_client(mocked_responses):
    ...