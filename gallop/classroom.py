from typing import Callable, Union


CLASS_ROOM = dict()
JSON_FRIENDLY = [str, float, int, bool, type(None)]


def to_classroom(x: Union[str, object]) -> Union[object, Callable]:
    """
    Register the class in the CLASS_ROOM
    """
    if type(x) == str:
        def wrapper(cls: object) -> object:
            CLASS_ROOM[x] = cls
            return cls
        return wrapper
    classname = x.__name__
    CLASS_ROOM[classname] = x
    return x


def cl(class_name: str) -> object:
    """
    Get the class from the CLASS_ROOM
    """
    if class_name not in CLASS_ROOM:
        raise ValueError(f"Class {class_name} not found")
    return CLASS_ROOM[class_name]
