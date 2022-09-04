from gallop.config import BaseConfig
from gallop.call import Caller
from gallop.classroom import to_classroom, cl
import logging
from subprocess import check_output
import os


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


def test_use_task():
    """
    Input data will be like
    [1, 2, 3, {"somekey": "somevalue"}]
    """
    func_config = BaseConfig.from_yaml("./test/use_task.yaml")
    Caller.resolve_item(func_config)

    reconstructed = cl("reconstructed_data")

    assert type(reconstructed) == list
    assert reconstructed[0] == 1
    assert reconstructed[1] == 2
    assert reconstructed[2] == 3
    assert reconstructed[3]["somekey"] == "somevalue"


def test_command_line():
    res = check_output("gallop test/use_task", shell=True)
    logging.info(res.decode())


def test_change_value():
    func_config = BaseConfig.from_yaml("./test/use_task.yaml")

    func_config.overwrite("simple_task.2.kwargs.b.0", 100)
    func_config.overwrite("simple_task.0.kwargs.string.args.0.0", 100)
    Caller.resolve_item(func_config)

    assert cl("reconstructed_data")[0] == 100


def test_env_checkout():
    func_config = BaseConfig.from_yaml("./test/env_checkout.yaml")
    Caller.resolve_item(func_config)

    assert cl("sys-user") == os.environ["USER"]
