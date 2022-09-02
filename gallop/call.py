from gallop.config import BaseConfig
from gallop.classroom import to_classroom, cl
from typing import (
    Any, Optional, Dict, List
    )
import json
import yaml
import logging
from pathlib import Path
from gallop.classroom import JSON_FRIENDLY, CLASS_ROOM


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
    def __init__(self, config: BaseConfig):
        self.config = config
        if "func_name" not in self.config:
            raise ValueError("func_name is required")

        self.args = self.config.get("args", [])
        self.kwargs = self.config.get("kwargs", {})

        self.callable = cl(self.config.func_name)

        self.checkin = self.config.get("checkin", None)

    @classmethod
    def run_list(cls, some_list: List[Any]) -> List[Any]:
        for i, item in enumerate(some_list):
            if type(item) in (dict, BaseConfig):
                if "func_name" in item:
                    some_list[i] = cls(item)()
                else:
                    some_list[i] = cls.run_dict(item)
                continue
            if type(item) is list:
                some_list[i] = cls.run_list(item)
        return some_list

    @classmethod
    def run_dict(cls, some_dict: Dict[str, Any]) -> Dict[str, Any]:
        for key, value in some_dict.items():
            if type(value) in (dict, BaseConfig):
                if "func_name" in value:
                    logging.info(f"✨ Running {key} as function")
                    some_dict[key] = cls(value)()
                elif "checkout" in value:
                    logging.info(f"👀 Checking out {key}")
                    some_dict[key] = cl(value.checkout)
                else:
                    some_dict[key] = cls.run_dict(value)
                continue
            if type(value) is list:
                some_dict[key] = cls.run_list(value)
        return some_dict

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


@to_classroom("Field")
class Field(conf_mixin_factory("Field")):
    def __init__(
        self,
        name: str,
        typing: str = "str",
        attrs: Optional[Dict[str, Any]] = dict(),
        description: Optional[str] = None,
    ):
        self.config = BaseConfig()
        self.config.name = name
        self.config.typing = typing
        if description is not None:
            self.config.description = description
        if attrs is not None:
            self.config.fields = attrs

    def validate(self, obj: Any):
        """
        Validate an object
        """
        if self.config.typing != "Any":
            if isinstance(
                obj,
                cl(self.config.typing),
            ):
                return
            # check for subclass inheritance
            elif issubclass(
                cl(self.config.typing),
                type(obj),
            ) or issubclass(
                type(obj),
                cl(self.config.typing),
            ):
                return
            else:
                raise TypeError(
                    f"Field {self.config.name} should be "
                    f"{self.config.typing}, but got {type(obj)}")


def GiantSave(obj: Any, field: Field) -> BaseConfig:
    # match for very basic types
    if type(obj) in JSON_FRIENDLY:
        return obj

    return_dict = dict()
    if "attrs" in field:
        for attr, sub_field in field.attrs.items():
            if hasattr(obj, attr) is False:
                continue
            val = obj.__getattribute__(attr)
            if type(val) in JSON_FRIENDLY:
                return_dict[attr] = val
            else:
                return_dict[attr] = GiantSave(val, sub_field)

    return BaseConfig(**return_dict)
