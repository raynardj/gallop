from typing import Callable, Any
from gallop.classroom import to_classroom, CLASS_ROOM
import logging


@to_classroom("Importer")
def Importer(imports: str) -> Callable:
    """
    import a class or a function, something callable
    from a string splited by dot

    return a callable
    """
    if imports in CLASS_ROOM:
        logging.debug(f"⚡️ read {imports} from CACHE")
        return CLASS_ROOM[imports]
    import_list = imports.split('.')
    if len(import_list) == 0:
        raise ImportError(f"Invalid import string: {imports}")
    elif len(import_list) == 1:
        # import a module
        module = __import__(import_list[0])
        # save to cache
        logging.debug(f"🔌 CACHING {imports}")
        to_classroom(imports)(module)
        return module
    else:
        # longer sequence of module
        # import the root module first
        package = __import__(import_list[0])

        # import the part down the chain
        for module in import_list[1:]:
            package = getattr(package, module)

        # save to cache
        logging.debug(f"🔌 CACHING {imports}")
        to_classroom(imports)(package)
        return package


def write_file(string: str, filename: str) -> None:
    """
    save a string to a file
    """
    with open(filename, "w") as f:
        f.write(string)


def read_file(filename: str) -> str:
    """
    load a string from a file
    """
    with open(filename, "r") as f:
        return f.read()


def equal_assertion(a, b) -> None:
    """
    assert two things are equal
    """
    assert a == b, f"{a} != {b}"


def checkin_value(key: str, value: Any) -> None:
    """
    save a value to CLASS_ROOM
    """
    CLASS_ROOM[key] = value
