from typing import Callable
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
