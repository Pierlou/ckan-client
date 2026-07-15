import logging

from .client import CkanClient, check_kwargs


def assert_auth(client: CkanClient) -> None:
    if not client._authenticated:
        raise PermissionError(
            "This method requires authentication, please specify your API key in the Client"
        )


class BaseObject:
  id: str
  _name: str
  _attrs: dict | None
  _deleted: bool = False

  def __init__(self, id: str, *, _client: CkanClient, _from_reponse: dict | None = None):
    if self.__class__.__name__ == "BaseObject":
      raise TypeError("BaseObject is an abstract class, it cannot be instanciated")
    self.id = id
    self._client = _client
    self._name = self.__class__.__name__.lower()
    if _from_reponse is not None:
      self._attrs = _from_reponse
    elif self._client.fetch:
      self._fetch_metadata()

  def _fetch_metadata(self):
    # not the best if the object is updated by another means in between but fair enough
    if self._attrs is None:
      self._attrs = getattr(self._client.rckan.action, f"{self._name}_show")(id=self.id)

  def _raise_if_deleted(self):
    if self.deleted:
      raise TypeError(f"This {self._name} has been deleted")

  def __getattr__(self, value: str):
    self._raise_if_deleted()
    if value in dir(self):
        return getattr(self, value)
    self._fetch_metadata()
    if value not in self._attrs:
        raise AttributeError(
            f"`{value}` is not a valid {self._name} attribute. The available attributes are: {list(self._attrs.keys())}"
        )
    return self._attrs[value]

  def __repr__(self) -> str:
    self._raise_if_deleted()
    return str(self._attrs)

  def patch(self, payload: dict) -> None:
    if self.deleted:
        raise TypeError(f"This {self._name} has been deleted")
    assert_auth(self._client)
    check_kwargs(payload, self._client._obj_params[self._name])
    if self._client.verbose:
        logging.info(f"🔁 Putting {self.id} with {payload}")
    self._attrs = getattr(self._client.rckan.action, f"{self._name}_patch")(id=self.id, **payload)

  def delete(self) -> None:
    if self.deleted:
        raise TypeError(f"This {self._name} has been deleted")
    assert_auth(self._client)
    if self._client.verbose:
        logging.info(f"🚮 Deleting {self.id}")
    getattr(self._client.rckan.action, f"{self._name}_delete")(id=self.id)
    self.deleted = True
