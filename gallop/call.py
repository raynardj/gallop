from gallop.config import BaseConfig
from gallop.classroom import to_classroom, cl
from typing import Any, Optional
import json
import yaml
from pathlib import Path


def conf_mixin_factory(class_name: str) -> object:
    class ConfMixin:
        f"""
        Use the {class_name}ConfMixin as a Mixin class,
        for {class_name} class
        This will bound with properties related to config
        """

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
            with open(json_path, "w") as f:
                json.dump(self.config.conf_data, f)

        def to_yaml(self, yaml_path: Path):
            with open(yaml_path, "w") as f:
                yaml.safe_dump(self.config.conf_data, f)

    ConfMixin.__name__ = f"{class_name}ConfMixin"

    # register the class in the CLASS_ROOM
    to_classroom(ConfMixin.__name__)(ConfMixin)
    return ConfMixin


@to_classroom("GallopField")
class Field(conf_mixin_factory("Field")):
    def __init__(
        self,
        name: str,
        typing: str = "str",
        conf_type: str = "Field",
        default: Optional[Any] = None,
        required: bool = True,
        description: Optional[str] = None,
    ):
        self.config = BaseConfig()
        self.config.name = name
        self.config.conf_type = conf_type
        if default is not None:
            self.config.default = default
        self.config.typing = typing
        self.config.required = required
        if description is not None:
            self.config.description = description

    def __repr__(self):
        return json.dumps(
            self.config.conf_data, indent=2)

    def validate(self, base_config: BaseConfig):
        if self.config.name not in base_config:
            if self.config.required:
                raise ValueError(
                    f"Field {self.config.name} is required")

    def __call__(self, *args, **kwargs):
        """
        Substantiate a field value
        """
        cls = cl(self.config.typing)
        return cls(*args, **kwargs)
