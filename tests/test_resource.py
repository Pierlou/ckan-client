from unittest.mock import Mock

import pytest

from ckan_client import CkanClient, Resource, Package

from conftest import CKAN_URL, RESOURCE_ID, package_metadata, resource_metadata


def test_resource_read_only(mock_help):
    ckanc = CkanClient(CKAN_URL)
    ckanc.rckan.action.resource_show = Mock(return_value=resource_metadata)
    res = ckanc.resource(RESOURCE_ID)
    assert isinstance(res, Resource)
    for k, v in resource_metadata.items():
        assert getattr(res, k) == v
    assert res._name == "resource"
    assert res._deleted is False
    with pytest.raises(PermissionError):
        res.patch({"a": 1})
    with pytest.raises(PermissionError):
        res.delete()


def test_resource_authenticated(mock_help):
    ckanc = CkanClient(CKAN_URL, apikey="s3cr3t")
    ckanc.rckan.action.resource_show = Mock(return_value=resource_metadata)
    res = ckanc.resource(RESOURCE_ID)
    # testing patch
    payload = {"description": "modified", "upload": "pretend it's a file"}
    ckanc.rckan.action.resource_patch = Mock(return_value=resource_metadata | payload)
    res.patch(payload)
    # checking that the object has been modified too
    for k, v in payload.items():
        assert getattr(res, k) == v
    # testing delete
    ckanc.rckan.action.resource_delete = Mock(return_value=None)
    res.delete()
    # now it's not possible to patch nor delete
    with pytest.raises(TypeError):
        res.patch({"a": 1})
    with pytest.raises(TypeError):
        res.delete()


def test_resource_patch_bad_payload(mock_help):
    ckanc = CkanClient(CKAN_URL, apikey="s3cr3t")
    ckanc.rckan.action.resource_show = Mock(return_value=resource_metadata)
    res = ckanc.resource(RESOURCE_ID)
    with pytest.raises(ValueError):
        res.patch({"not_a_prop": True})


def test_resource_package(mock_help):
    ckanc = CkanClient(CKAN_URL)
    ckanc.rckan.action.resource_show = Mock(return_value=resource_metadata)
    res = ckanc.resource(RESOURCE_ID)
    ckanc.rckan.action.package_show = Mock(return_value=package_metadata)
    pack = res.package
    assert isinstance(pack, Package) and pack.id == res.package_id
