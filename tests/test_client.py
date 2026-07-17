import pytest

from ckan_client.client import CkanClient, check_kwargs

from conftest import CKAN_URL


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


@pytest.mark.parametrize(
    "apikey",
    [None, "secret_key"],
)
def test_client(mock_help, apikey):
    ckanc = CkanClient(CKAN_URL, apikey=apikey)
    if apikey is None:
        assert ckanc._authenticated is False
        with pytest.raises(PermissionError):
            ckanc._assert_auth()
    else:
        assert ckanc._authenticated is True
        ckanc._assert_auth()

    for obj in ckanc._obj:
        assert obj in dir(ckanc)
        assert f"create_{obj}" in dir(ckanc)
        assert obj in ckanc._obj_params
        assert all(
            isinstance(v, dict)
            and all(k in v for k in ["type", "description", "optional"])
            for v in ckanc._obj_params[obj].values()
        )
