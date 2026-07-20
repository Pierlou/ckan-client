from unittest.mock import Mock

import pytest
from conftest import CKAN_URL

from ckan_client import CkanClient, Organization, Package, Resource
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
            isinstance(v, dict) and all(k in v for k in ["type", "description", "optional"])
            for v in ckanc._obj_params[obj].values()
        )


@pytest.mark.parametrize(
    "obj_class, payload",
    [
        (Organization, {"name": "My orga", "description": "Short description"}),
        (Package, {"name": "A new dataset", "private": True, "tags": ["test"]}),
        (Resource, {"name": "New resource", "upload": "an open file", "mimetype": "text/csv"}),
    ],
)
def test_client_create_obj(mock_help, obj_class, payload):
    ckanc = CkanClient(CKAN_URL, apikey="s3cr3t")
    _id = "abcd"
    _name = obj_class.__name__.lower()
    setattr(
        ckanc.rckan.action,
        f"{_name}_create",
        Mock(return_value=payload | {"id": _id}),
    )
    created = getattr(ckanc, f"create_{_name}")(payload)
    assert isinstance(created, obj_class)
    assert created.id == _id
    for k, v in payload.items():
        assert getattr(created, k) == v
