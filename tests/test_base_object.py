import pytest

from ckan_client.base_object import BaseObject


def test_base_object_not_instanciable():
    with pytest.raises(TypeError):
        BaseObject("abcd")
