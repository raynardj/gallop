from gallop.config import BaseConfig
from gallop.call import Caller
from gallop.classroom import to_classroom, cl
import logging


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
    logging.info("start resolving")

    Caller.resolve_item(func_config)

    result2 = cl("result2")
    assert result2.name == "D"
    assert result2.kwargs["charlie"] == 2

    logging.debug("'checkout' example")
    delta = result2.kwargs["delta"]
    assert delta.kwargs['name'] == "B"
    assert delta.kwargs['bravo'] == "kwarg2"

    logging.debug("recursive 'checkout' example")
    args2 = delta.args[2]
    assert args2.kwargs['name'] == "A"
