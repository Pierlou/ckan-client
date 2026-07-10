import re

from ckanapi import RemoteCKAN
import niquests


def build_params(doctring: str) -> dict:
    # building a clean dict of valid kwargs with details (type, description, optional) from the fetched docstring
    param_pattern = re.compile(r":param (\w+): (.*?)(?=\n\s*:param|\n\s*:type|\Z)", re.DOTALL)
    type_pattern = re.compile(r":type (\w+): (.*?)(?=\n\s*:param|\n\s*:type|\Z)", re.DOTALL)
    params = param_pattern.findall(doctring)
    types = type_pattern.findall(doctring)
    result = {}
    for (param, desc), (_, type_) in zip(params, types):
        clean_desc = " ".join(desc.replace("(optional)", "").split())
        is_optional = "optional" in desc.lower()
        result[param] = {
            "type": type_.strip(),
            "description": clean_desc,
            "optional": is_optional,
        }
    return result


def check_kwargs(given_kwargs: dict, allowed_kwargs: dict) -> None:
    if any(k not in allowed_kwargs for k in given_kwargs):
        raise ValueError(f"Allowed kwargs are: {', '.join(allowed_kwargs.keys())}")
    if any(k not in given_kwargs for k in [arg for arg, doc in allowed_kwargs.items() if not doc["optional"]]):
        raise ValueError(
            f"The following kwargs are mandatory: {', '.join(arg for arg, doc in allowed_kwargs.items() if not doc['optional'])}"
        )


def create_method(obj: str, allowed_kwargs: dict, rckan: RemoteCKAN):
    def _m(**kwargs):
        check_kwargs(kwargs, allowed_kwargs)
        getattr(rckan.action, f"{obj}_create")(**kwargs)
    return _m


class CkanClient:
    _obj: set[str] = {
        "package",
        "resource",
    }

    def __init__(self, base_url: str, apikey : str | None = None, *, verbose: bool = True):
        self._authenticated = apikey is not None
        self.rckan = RemoteCKAN(base_url, apikey=apikey)
        self._obj_params = {}
        for obj in self._obj:
            # fetching the valid kwargs from the doc endpoints
            self._obj_params[obj] = build_params(
                niquests.get(
                    f"{base_url}/api/3/action/help_show?name={obj}_create"
                ).json()["result"]
            )
            # re-implements the object creation with a stricter kwargs check
            setattr(
                self,
                f"{obj}_create",
                create_method(obj, self._obj_params[obj], self.rckan),
            )
