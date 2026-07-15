from .base_object import BaseObject


class Resource(BaseObject):
    @property
    def package(self):
        from .package import Package

        self._fetch_metadata()
        return Package(
            id_self._attrs["package_id"],
            _client=self._client,
        )
