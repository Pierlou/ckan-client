import logging
from typing import TYPE_CHECKING

from .base_object import BaseObject
from .client import check_kwargs

if TYPE_CHECKING:
    from .package import Package


class Organization(BaseObject):
    @property
    def packages(self) -> "list[Package]":
        from .package import Package

        self._fetch_metadata()
        return [
            Package(
                id=p["id"],
                _client=self._client,
                _from_response=p,
            )
            for p in self._client.rckan.action.organization_show(
                id=self.id,
                include_datasets=True,
            )["packages"]
        ]

    def create_package(self, payload: dict) -> "Package":
        from .package import Package

        self._client._assert_auth()
        if "owner_org" in payload:
            raise AttributeError(
                "The `owner_org` argument should not be specified when creating a package from an organization"
            )
        check_kwargs(payload, self._client._obj_params["package"])
        if self._client.verbose:
            logging.info(f"🆕 Creating a new package with {payload}")
        resp = self._client.rckan.action.package_create(**(payload | {"owner_org": self.id}))
        return Package(id=resp["id"], _from_response=resp, _client=self._client)
