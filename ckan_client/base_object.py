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

  def __init__(self, id: str, *, _client: CkanClient, attrs: dict | None = None, fetch: bool = True):
    if self.__class__.__name__ == "BaseObject":
        raise TypeError("BaseObject is an abstract class, it cannot be instanciated")
    self.id = id
    self._client = _client
    self._name = self.__class__.__name__.lower()
    self._attrs = (
      attrs
      if attrs is not None or not fetch
      else getattr(self._client.rckan.action, f"{self._name}_show")(id=self.id)
    )

  def __getattr__(self, value: str):
    if self.deleted:
        raise TypeError(f"This {self._name} has been deleted")
    return self._attrs[value]

  def __repr__(self) -> str:
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
