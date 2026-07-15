from .base_object import BaseObject
from .resource import Resource


class Package(BaseObject):
    @property
    def resources(self):
        self._fetch_metadata()
        for res in self._attrs["resources"]:
            yield Resource(
                id=res["id"],
                _client=self._client,
                _from_response=res,
            )
