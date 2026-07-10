from .client import CkanClient, check_kwargs


def assert_auth(client: CkanClient) -> None:
    if not client._authenticated:
        raise PermissionError(
            "This method requires authentication, please specify your API key in the Client"
        )


class BaseObject:
  def __init__(self, id: str, _client: CkanClient, attrs: dict | None = None):
    if self.__class__.__name__ == "BaseObject":
        raise TypeError("BaseObject is an abstract class, it cannot be instanciated")
    self.id = id
    self._client = _client
    self._name = self.__class__.__name__.lower()
    self._attrs = (
      attrs
      if attrs is not None
      else getattr(self._client.rckan.action, f"{self._name}_show")(id=self.id)
    )

  def __getattr__(self, value: str):
    return self._attrs.get(value)

  def __repr__(self) -> str:
    return str(self._attrs)

  def patch(self, payload: dict):
    assert_auth(self._client)
    check_kwargs(payload, self._client._obj_params[self._name])
    return getattr(self._client.rckan.action, f"{self._name}_patch")(id=self.id, **payload)

  def delete(self):
    getattr(self._client.rckan.action, f"{self._name}_delete")(id=self.id)
    
