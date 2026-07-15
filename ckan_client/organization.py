from typing import TYPE_CHECKING

from .base_object import BaseObject

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
            )
        ]
