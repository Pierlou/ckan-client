import logging

from .client import CkanClient, check_kwargs


class BaseObject:
    id: str
    _name: str
    _attrs: dict | None
    _deleted: bool = False

    def __init__(self, id: str, *, _client: CkanClient, _from_response: dict | None = None):
        if self.__class__.__name__ == "BaseObject":
            raise TypeError("BaseObject is an abstract class, it cannot be instanciated")
        self.id = id
        self._client = _client
        self._name = self.__class__.__name__.lower()
        if _from_response is not None:
            self._attrs = _from_response
        elif self._client.fetch:
            self._fetch_metadata()

    def _fetch_metadata(self):
        # not the best if the object is updated by another means in between but fair enough
        try:
            attrs = object.__getattribute__(self, "_attrs")
            if attrs is not None:
                return
        except AttributeError:
            pass
        object.__setattr__(
            self,
            "_attrs",
            getattr(
                self._client.rckan.action,
                f"{object.__getattribute__(self, '_name')}_show",
            )(id=object.__getattribute__(self, 'id'))
        )

    def _raise_if_deleted(self):
        if self._deleted:
            raise TypeError(f"This {self._name} has been deleted")

    def __getattr__(self, value: str):
        if value in dir(self):
            return object.__getattribute__(self, value)
        self._fetch_metadata()
        attrs = object.__getattribute__(self, "_attrs")
        if value not in attrs:
            raise AttributeError(
                f"`{value}` is not a valid {object.__getattribute__(self, '_name')} attribute. The available attributes are: {list(attrs.keys())}"
            )
        return attrs[value]

    def __repr__(self) -> str:
        self._raise_if_deleted()
        return str(object.__getattribute__(self, "_attrs"))

    def patch(self, payload: dict) -> None:
        self._raise_if_deleted()
        self._client._assert_auth()
        check_kwargs(payload, self._client._obj_params[self._name])
        if self._client.verbose:
            logging.info(f"🔁 Putting {self.id} with {payload}")
        self._attrs = getattr(self._client.rckan.action, f"{self._name}_patch")(
            id=self.id, **payload
        )

    def delete(self) -> None:
        self._raise_if_deleted()
        self._client._assert_auth()
        if self._client.verbose:
            logging.info(f"🚮 Deleting {self.id}")
        getattr(self._client.rckan.action, f"{self._name}_delete")(id=self.id)
        self._deleted = True
