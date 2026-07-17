from unittest.mock import Mock

import pytest

from ckan_client import CkanClient, Organization, Package, Resource

from conftest import CKAN_URL, PACKAGE_ID, package_metadata, organization_metadata, resource_metadata


def test_package_read_only(mock_help):
    ckanc = CkanClient(CKAN_URL)
    ckanc.rckan.action.package_show = Mock(return_value=package_metadata)
    pack = ckanc.package(PACKAGE_ID)
    assert isinstance(pack, Package)
    for k, v in package_metadata.items():
        if k not in {"organization", "resources"}:
            assert getattr(pack, k) == v
    assert pack._name == "package"
    assert pack._deleted is False
    with pytest.raises(PermissionError):
        pack.patch({"a": 1})
    with pytest.raises(PermissionError):
        pack.delete()


def test_package_authenticated(mock_help):
    ckanc = CkanClient(CKAN_URL, apikey="s3cr3t")
    ckanc.rckan.action.package_show = Mock(return_value=package_metadata)
    pack = ckanc.package(PACKAGE_ID)
    # testing patch
    payload = {"title": "modified", "notes": "insights..."}
    ckanc.rckan.action.package_patch = Mock(return_value=package_metadata | payload)
    pack.patch(payload)
    # checking that the object has been modified too
    for k, v in payload.items():
        assert getattr(pack, k) == v
    # testing delete
    ckanc.rckan.action.package_delete = Mock(return_value=None)
    pack.delete()
    # now it's not possible to patch nor delete
    with pytest.raises(TypeError):
        pack.patch({"a": 1})
    with pytest.raises(TypeError):
        pack.delete()


def test_package_patch_bad_payload(mock_help):
    ckanc = CkanClient(CKAN_URL, apikey="s3cr3t")
    ckanc.rckan.action.package_show = Mock(return_value=package_metadata)
    pack = ckanc.package(PACKAGE_ID)
    with pytest.raises(ValueError):
        pack.patch({"not_a_prop": True})


def test_package_orga(mock_help):
    ckanc = CkanClient(CKAN_URL)
    ckanc.rckan.action.package_show = Mock(return_value=package_metadata)
    pack = ckanc.package(PACKAGE_ID)
    ckanc.rckan.action.organization_show = Mock(return_value=organization_metadata)
    orga = pack.organization
    assert isinstance(orga, Organization) and orga.id == package_metadata["organization"]["id"]


def test_package_resources(mock_help):
    ckanc = CkanClient(CKAN_URL)
    ckanc.rckan.action.package_show = Mock(return_value=package_metadata)
    pack = ckanc.package(PACKAGE_ID)
    resources = pack.resources
    assert isinstance(resources, list) and len(resources) == len(package_metadata["resources"]) and all(isinstance(r, Resource) for r in resources)


def test_package_create_resource(mock_help):
    ckanc = CkanClient(CKAN_URL, apikey="s3cr3t")
    ckanc.rckan.action.package_show = Mock(return_value=package_metadata)
    pack = ckanc.package(PACKAGE_ID)
    payload = {"name": "brand_new_resource", "upload": "pretend it's a file"}
    ckanc.rckan.action.resource_create = Mock(return_value=payload | {"id": resource_metadata["id"]})
    res = pack.create_resource(payload)
    assert isinstance(res, Resource)
    assert res.id == resource_metadata["id"]
    for k, v in payload.items():
        assert getattr(res, k) == v

    # test to pass package_id, should fail
    with pytest.raises(AttributeError):
        res = pack.create_resource(payload | {"package_id": "another-pack"})
