from gallop.config import BaseConfig
from gallop.classroom import to_classroom, cl
from typing import (
    Any, Dict, List, Union
)
import json
import yaml
import logging
from pathlib import Path
from gallop.classroom import CLASS_ROOM


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
    def __init__(self, config: BaseConfig,):
        self.config = config
        if "func_name" not in self.config:
            raise ValueError("func_name is required")

        self.callable = cl(self.config.func_name)

        self.args = self.config.get("args", [])
        self.kwargs = self.config.get("kwargs", {})
        self.checkin = self.config.get("checkin", None)

    @classmethod
    def run_list(cls, some_list: List[Any]) -> List[Any]:
        return_list = list()
        for item in some_list:
            # recurse into dict
            if type(item) in (dict, BaseConfig):
                if "func_name" in item:
                    if type(item) == dict:
                        item = BaseConfig(**item)
                    return_list.append(cls(item,)())
                else:
                    return_list.append(cls.run_dict(item))
            # recurse into list
            elif type(item) is list:
                return_list.append(cls.run_list(item))
            # default case
            else:
                return_list.append(item)
        return return_list

    @classmethod
    def run_dict(
        cls,
        some_dict: Union[Dict[str, Any], BaseConfig],
    ) -> Dict[str, Any]:
        return_dict = dict()
        for key, value in some_dict.items():
            if type(value) in (dict, BaseConfig):
                if "func_name" in value:
                    logging.info(f"✨ Running {key} as function")
                    if type(value) == dict:
                        value = BaseConfig(**value)
                    return_dict[key] = cls(value)()
                elif "checkout" in value:
                    logging.info(f"👀 Checking out {key}")
                    return_dict[key] = cl(value.checkout)
                else:
                    return_dict[key] = cls.run_dict(value)
            elif type(value) is list:
                return_dict[key] = cls.run_list(value)
            else:
                return_dict[key] = value
        return return_dict

    def __call__(self) -> Any:
        """
        Execute the function
        """
        self.args = self.run_list(self.args)
        self.kwargs = self.run_dict(self.kwargs)
        res = self.callable(*self.args, **self.kwargs)

        # register the result back to checkout
        if self.checkin is not None:
            if self.checkin in CLASS_ROOM:
                logging.warning(f"💫 Overwriting Name: {self.checkin}")
            to_classroom(self.checkin)(res)
        return res
