import json

import pytest
import responses

from ckan_client import CkanClient


CKAN_URL = "https://ckan.data.example.fr"
ORGANIZATION_ID = "e9d6a73f-dd4d-4c89-abe4-be24d31b9239"
PACKAGE_ID = "e585b3d4-3c5b-4b95-948e-6f6ec27e922a"
RESOURCE_ID = "e7a249c8-cfc9-4608-b5d2-ef0541255ba9"

with open("tests/package_metadata.json", "r") as f:
    package_metadata = json.load(f)

with open("tests/resource_metadata.json", "r") as f:
    resource_metadata = json.load(f)

with open("tests/organization_metadata.json", "r") as f:
    organization_metadata = json.load(f)

with open("tests/help_data.json", "r") as f:
    help_data = json.load(f)


@pytest.fixture
def mock_help():
    with responses.RequestsMock() as rsps:
        for obj in CkanClient._obj:
            rsps.get(
                f"{CKAN_URL}/api/3/action/help_show?name={obj}_create",
                json=help_data[obj],
                status=200,
            )
        yield rsps
