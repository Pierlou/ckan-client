from unittest.mock import Mock

import pytest

from ckan_client import CkanClient, Organization, Package

from conftest import CKAN_URL, ORGANIZATION_ID, package_metadata, organization_metadata


def test_orga_read_only(mock_help):
    ckanc = CkanClient(CKAN_URL)
    ckanc.rckan.action.organization_show = Mock(return_value=organization_metadata)
    orga = ckanc.organization(ORGANIZATION_ID)
    assert isinstance(orga, Organization)
    for k, v in organization_metadata.items():
        assert getattr(orga, k) == v
    assert orga._name == "organization"
    assert orga._deleted is False
    with pytest.raises(PermissionError):
        orga.patch({"a": 1})
    with pytest.raises(PermissionError):
        orga.delete()


def test_orga_authenticated(mock_help):
    ckanc = CkanClient(CKAN_URL, apikey="s3cr3t")
    ckanc.rckan.action.organization_show = Mock(return_value=organization_metadata)
    orga = ckanc.organization(ORGANIZATION_ID)
    # testing patch
    payload = {"description": "modified", "title": "New title"}
    ckanc.rckan.action.organization_patch = Mock(return_value=organization_metadata | payload)
    orga.patch(payload)
    # checking that the object has been modified too
    for k, v in payload.items():
        assert getattr(orga, k) == v
    # testing delete
    ckanc.rckan.action.organization_delete = Mock(return_value=None)
    orga.delete()
    # now it's not possible to patch nor delete
    with pytest.raises(TypeError):
        orga.patch({"a": 1})
    with pytest.raises(TypeError):
        orga.delete()


def test_orga_patch_bad_payload(mock_help):
    ckanc = CkanClient(CKAN_URL, apikey="s3cr3t")
    ckanc.rckan.action.organization_show = Mock(return_value=organization_metadata)
    orga = ckanc.organization(ORGANIZATION_ID)
    with pytest.raises(ValueError):
        orga.patch({"not_a_prop": True})


def test_orga_packages(mock_help):
    ckanc = CkanClient(CKAN_URL)
    ckanc.rckan.action.organization_show = Mock(return_value=organization_metadata)
    orga = ckanc.organization(ORGANIZATION_ID)
    nb_packages = 3 
    ckanc.rckan.action.organization_show = Mock(
        return_value=organization_metadata | {"packages": [package_metadata for _ in range(nb_packages)]}
    )
    packs = orga.packages
    assert isinstance(packs, list) and len(packs) == nb_packages and all(isinstance(p, Package) for p in packs)


def test_orga_create_package(mock_help):
    ckanc = CkanClient(CKAN_URL, apikey="s3cr3t")
    ckanc.rckan.action.organization_show = Mock(return_value=organization_metadata)
    orga = ckanc.organization(ORGANIZATION_ID)
    payload = {"name": "brand_new_package", "title": "TITLE"}
    ckanc.rckan.action.package_create = Mock(return_value=payload | {"id": package_metadata["id"]})
    pack = orga.create_package(payload)
    assert isinstance(pack, Package)
    assert pack.id == package_metadata["id"]
    for k, v in payload.items():
        assert getattr(pack, k) == v
