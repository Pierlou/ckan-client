from typing import TYPE_CHECKING

from .base_object import BaseObject

if TYPE_CHECKING:
    from .package import Package


class Resource(BaseObject):
    @property
    def package(self) -> "Package":
        from .package import Package

        self._fetch_metadata()
        return Package(
            id=self._attrs["package_id"],
            _client=self._client,
        )
