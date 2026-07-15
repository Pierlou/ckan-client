import logging
import re
from importlib.metadata import version
from typing import TYPE_CHECKING, Callable

import requests
from ckanapi import RemoteCKAN

if TYPE_CHECKING:
    from .package import Package
    from .resource import Resource

USER_AGENT = f"ckan-client/{version('ckan-client')}"


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


def check_kwargs(given_kwargs: dict | None, allowed_kwargs: dict) -> None:
    if given_kwargs is None:
        return
    if any(k not in allowed_kwargs for k in given_kwargs):
        raise ValueError(f"Allowed kwargs are: {', '.join(allowed_kwargs.keys())}")
    # the optional fields seem off, like plugin_data for package is not optional (but it's possible to create a package without specifying it)


#    if any(
#        k not in given_kwargs
#        for k in [arg for arg, doc in allowed_kwargs.items() if not doc["optional"]]
#    ):
#        raise ValueError(
#            f"The following kwargs are mandatory: {', '.join(arg for arg, doc in allowed_kwargs.items() if not doc['optional'])}"
#        )


class CkanClient:
    _obj: set[str] = {
        "package",
        "resource",
        "organization",
    }

    def __init__(
        self,
        base_url: str,
        apikey: str | None = None,
        *,
        user_agent: str = USER_AGENT,
        verbose: bool = True,
        fetch: bool = True,  # whether or not to request metadata on object instanciation, useful when you only want to patch/delete
    ):
        self._authenticated = apikey is not None
        self.rckan = RemoteCKAN(base_url, apikey=apikey, user_agent=user_agent)
        self._obj_params = {}
        self.verbose = verbose
        self.fetch = fetch
        for obj in self._obj:
            # fetching the valid kwargs from the doc endpoints
            self._obj_params[obj] = build_params(
                requests.get(f"{base_url}/api/3/action/help_show?name={obj}_create").json()[
                    "result"
                ]
            )
            # re-implements the object creation with a stricter kwargs check
            setattr(
                self,
                f"{obj}_create",
                create_method(obj=obj, allowed_kwargs=self._obj_params[obj], client=self),
            )
            setattr(
                self,
                obj,
                obj_method(obj=obj, allowed_kwargs=self._obj_params[obj], client=self),
            )


def create_method(obj: str, allowed_kwargs: dict, client: "CkanClient") -> Callable:
    def _m(**kwargs) -> "Package | Resource":
        check_kwargs(kwargs, allowed_kwargs)
        if client.verbose:
            logging.info(f"🆕 Creating a new {obj} with {kwargs}")
        resp = getattr(client.rckan.action, f"{obj}_create")(**kwargs)
        match obj:
            # slightly overkill but futureproof
            case "package":
                from .package import Package

                return Package(id=resp["id"], _from_response=resp, _client=client)
            case "resource":
                from .resource import Resource

                return Resource(id=resp["id"], _from_response=resp, _client=client)
            case "organization":
                from .organization import Organization

                return Organization(id=resp["id"], _from_response=resp, _client=client)
            case _:
                raise NotImplementedError

    return _m


def obj_method(obj: str, allowed_kwargs: dict, client: "CkanClient") -> Callable:
    def _m(id: str, *, _from_response: dict | None = None) -> "Package | Resource":
        check_kwargs(_from_response, {k: v for k, v in allowed_kwargs.items() if k != "package_id"})
        match obj:
            # slightly overkill but futureproof
            case "package":
                from .package import Package

                return Package(id=id, _from_response=_from_response, _client=client)
            case "resource":
                from .resource import Resource

                return Resource(id=id, _from_response=_from_response, _client=client)
            case "organization":
                from .organization import Organization

                return Organization(id=id, _from_response=_from_response, _client=client)
            case _:
                raise NotImplementedError

    return _m
