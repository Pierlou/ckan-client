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

    def create_resource(self, payload: dict) -> "Resource":
        from .resource import Resource

        self._client._assert_auth()
        if "package_id" in payload:
            raise AttributeError(
                "The `package_id` argument should not be specified when creating a resource from a package"
            )
        check_kwargs(payload, self._client._obj_params["resource"])
        if self._client.verbose:
            logging.info(f"🆕 Creating a new resource with {payload}")
        resp = self._client.rckan.action.resoure_create(**(payload | {"package_id": self.id}))
        return Resource(id=resp["id"], _from_response=resp, _client=self._client)
