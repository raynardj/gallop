from gallop.config import BaseConfig
from gallop.classroom import to_classroom, cl
from gallop.funcs import Importer
from gallop.classroom import CLASS_ROOM, mark_sn
from typing import (
    Any, Dict, List
)
import json
import yaml
import logging
from datetime import datetime
from pathlib import Path
import traceback as tb
import os


def conf_mixin_factory(class_name: str) -> object:
    class ConfMixin:
        is_conf_mixin = True

        f"""
        Use the {class_name}ConfMixin as a Mixin class,
        for {class_name} class
        This will bound with properties related to config
        """

        def __repr__(self):
            return json.dumps(
                self.config.conf_data, indent=2)

        @classmethod
        def from_json(cls, json_path: Path) -> class_name:
            f"""
            Instantiate the {class_name} from json file path
            """
            with open(json_path, "r") as f:
                data = json.load(f)
            return cls(**data)

        @classmethod
        def from_yaml(cls, yaml_path: Path) -> class_name:
            f"""
            Instantiate the {class_name} from yaml file path
            """
            with open(yaml_path, "r") as f:
                data = yaml.safe_load(f)
            return cls(**data)

        def to_json(self, json_path: Path):
            f"""
            Save the {class_name} to json file path
            """
            with open(json_path, "w") as f:
                json.dump(self.config.conf_data, f)

        def to_yaml(self, yaml_path: Path):
            f"""
            Save the {class_name} to yaml file path
            """
            with open(yaml_path, "w") as f:
                yaml.safe_dump(self.config.conf_data, f)

        def to_dict(self) -> Dict[str, Any]:
            f"""
            Return the {class_name} as a dict recurssively
            """
            result = dict()
            for key, value in self.config.conf_data.items():
                if value is None:
                    # not registering value if it is None
                    continue
                if hasattr(value, "is_conf_mixin") is False:
                    result[key] = value
                elif value.is_conf_mixin:
                    result[key] = value.to_dict()
                else:
                    result[key] = value.to_dict()
            return result

    ConfMixin.__name__ = f"{class_name}ConfMixin"

    # register the class in the CLASS_ROOM
    to_classroom(ConfMixin.__name__)(ConfMixin)
    return ConfMixin


@to_classroom("Caller")
class Caller:
    def __init__(
        self,
        config: BaseConfig,
        depth: int = 0
    ):
        self.config = config
        if "func_name" not in self.config:
            raise ValueError("func_name is required")

        self.depth = depth

        if self.config.func_name[:4] == "use:":
            logging.info(f"Using {self.config.func_name}")
            self.callable = Importer(self.config.func_name[4:])
        else:
            self.callable = cl(self.config.func_name)

        self.args = self.config.get("args", [])
        self.kwargs = self.config.get("kwargs", {})
        self.checkin = self.config.get("checkin", None)

    @staticmethod
    def checkout_val(val: str) -> Any:
        """
        checkout the value from CLASS_ROOM
        """
        if val in CLASS_ROOM:
            return CLASS_ROOM[val]

        # load enviroment variable
        if val[:4] == "env:":
            logging.debug(f"🌲 Loading env: {val[4:]}")
            return os.environ[val[4:]]
        val_list = val.split(".")
        if len(val_list) > 1:
            if val_list[0] in CLASS_ROOM:
                root_module = CLASS_ROOM[val_list[0]]
                for attr in val_list[1:]:
                    root_module = getattr(root_module, attr)
                return root_module
        raise ValueError(f"Cannot find {val} in CLASS_ROOM")

    @classmethod
    def resolve_item(cls, item: Any, depth: int = 0) -> Any:
        """
        Recursively resolve the item
        """
        if type(item) in (dict, BaseConfig):
            if "func_name" in item:
                # a function package
                if type(item) == dict:
                    item = BaseConfig(**item,)
                return cls(item, depth=depth)()
            elif "checkout" in item:
                # a checkout package
                return cls.checkout_val(item.checkout)
            else:
                # not a function package
                return cls.run_dict(item, depth=depth+1)
        # recurse into list
        elif type(item) is list:
            return cls.run_list(item, depth=depth+1)
        # default case
        else:
            return item

    @classmethod
    def run_list(cls, some_list: List[Any], depth: int = 0) -> List[Any]:
        return_list = list(
            cls.resolve_item(item, depth=depth)
            for item in some_list)
        return return_list

    @classmethod
    def run_dict(
        cls,
        some_dict: Dict[str, Any],
        depth: int = 0
    ) -> Dict[str, Any]:
        return_dict = dict(
            (key, cls.resolve_item(some_dict[key], depth=depth))
            for key in some_dict)
        return return_dict

    def checkin_value(self, res: Any, spacing: str = ""):
        """
        check-in the result to CLASS_ROOM
        """
        if self.checkin is not None:
            if self.checkin in CLASS_ROOM:
                logging.warning(f"{spacing}💫 Overwriting Name: {self.checkin}")
            logging.debug(f"{spacing}🍄 Checkin: {self.checkin} = {res}")
            to_classroom(self.checkin)(res)

    def __call__(self) -> Any:
        """
        Execute the function
        """
        spacing = "\t" * self.depth
        sn = mark_sn()
        logging.info(f"{spacing}🚀 Calling[🍔 {sn}]: {self.config.func_name}")
        # description
        description = self.config.get("description", None)
        logging.info(f"{spacing}| {description}")
        start_time = datetime.now()

        # process args and kwargs
        self.args = self.run_list(self.args, depth=self.depth+1)
        self.kwargs = self.run_dict(self.kwargs, depth=self.depth+1)

        # execute the calling
        try:
            res = self.callable(*self.args, **self.kwargs)
        except KeyboardInterrupt:
            raise KeyboardInterrupt("User Interrupted")
        except Exception as e:
            logging.error(f"{spacing}❌ [🍔 {sn}]: {e}")
            tb.print_exc()
            for i, arg in enumerate(self.args):
                logging.error(f"{spacing}❌ [ARG {i}]: {arg}")
            for key, value in self.kwargs.items():
                logging.error(f"{spacing}❌ [KWARG:{key}]: {value}")
            raise e

        # log timing
        end_time = datetime.now()
        delta = end_time - start_time
        logging.info(f"{spacing}[🏁 {sn}] {self.config.func_name} :⏱️ {delta}")

        # register the result back to checkout
        self.checkin_value(res, spacing)
        return res
