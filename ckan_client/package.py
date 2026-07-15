from .base_object import BaseObject
from .organization import Organization
from .resource import Resource


class Package(BaseObject):
    @property
    def resources(self) -> list[Resource]:
        self._fetch_metadata()
        return [
            Resource(
                id=res["id"],
                _client=self._client,
                _from_response=res,
            )
            for res in self._attrs["resources"]
        ]

    @property
    def organization(self) -> Organization:
        self._fetch_metadata()
        return Organization(
            id=self._attrs["organization"]["id"],
            _client=self._client,
        )
