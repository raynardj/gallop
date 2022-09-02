from gallop.config import BaseConfig
from gallop.call import Caller
from gallop.classroom import to_classroom, cl
import json


@to_classroom("Dummy1")
class Dummy1:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.name = kwargs['name']

    def __repr__(self,):
        return f"Dummy: {self.name}"

    def __str__(self):
        return self.__repr__()


def test_func_setting():
    func_config = BaseConfig.from_yaml("./test/func_setting.yaml")
    Caller.run_dict(func_config)

    result2 = cl("result2")
    assert result2.name == "D"
    assert result2.kwargs["charlie"] == 2

    delta = result2.kwargs["delta"]
    assert delta.kwargs['name'] == "B"
    assert delta.kwargs['bravo'] == "kwarg2"

    args2 = delta.args[2]
    assert args2.kwargs['name'] == "A"
