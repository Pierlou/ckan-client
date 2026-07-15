from .base_object import BaseObject


class Organization(BaseObject):
    @property
    def packages(self):
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
