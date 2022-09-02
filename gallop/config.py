from typing import Any, Dict
import json
import yaml
from gallop.classroom import to_classroom, JSON_FRIENDLY
import logging


@to_classroom
class BaseConfig:
    """
    The base configuration class for gallop application
    This is a new sort of dict, that you can treat like JSON syntax
    """
    def __init__(self, **kwargs):
        super().__setattr__("conf_data", dict())
        for k, v in kwargs.items():
            self.__setitem__(k, v)

    def __getattr__(self, key: str):
        conf_data = self.__getattribute__("conf_data")
        if key in conf_data:
            return conf_data[key]
        else:
            return super().__getattribute__(key)

    def __hasattr__(self, key: str):
        return super().__hasattr__(key)

    def __setattr__(self, key: str, value: Any):
        self[key] = value

    def __getitem__(self, key: str):
        if key not in self.conf_data:
            raise KeyError(f"Config has no key {key}")
        return self.conf_data[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self.conf_data.get(key, default)

    def __setitem__(self, key: str, value: Any):
        self.conf_data[key] = self.substantiate_recursive(value)

    def __contains__(self, key: str):
        return key in self.conf_data

    def __repr__(self) -> str:
        """
        The representation of the config is the json string
        This design will make recursive config possible
        """
        return json.dumps(self.to_dict(), indent=2)

    def __len__(self) -> int:
        return len(self.conf_data)

    def __iter__(self):
        return iter(self.conf_data)

    def items(self):
        return self.conf_data.items()

    def keys(self):
        return self.conf_data.keys()

    # save data to config file
    def to_json(self, path: str):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f)

    def to_yaml(self, path: str):
        with open(path, "w") as f:
            yaml.safe_dump(self.to_dict(), f)

    # load data from config file
    @classmethod
    def from_json(cls, path: str):
        with open(path, "r") as f:
            conf_data = json.load(f)
        return cls(**conf_data)

    @classmethod
    def from_yaml(cls, path: str):
        with open(path, "r") as f:
            conf_data = yaml.safe_load(f)
        return cls(**conf_data)

    def flatten_recursive(self, x: Any) -> Any:
        """
        Render to data recursively
        """
        if type(x) in JSON_FRIENDLY:
            return x
        if hasattr(x, "to_dict"):
            return x.to_dict()
        if type(x) in [tuple, set, list]:
            return [self.flatten_recursive(y) for y in x]
        if type(x) is dict:
            return {k: self.flatten_recursive(v) for k, v in x.items()}
        logging.warning(
            f"🫦 type {type(x)} not flattened properly")
        return x

    def substantiate_recursive(self, x: Any) -> Any:
        """
        Render dict to config object recursively
        """
        if type(x) in JSON_FRIENDLY:
            return x
        if type(x) == dict:
            return self.__class__(**x)
        if type(x) in [tuple, set, list]:
            return [self.substantiate_recursive(y) for y in x]
        logging.warning(
            f"🍕 type {type(x)} not substantiated properly")
        return x

    def to_dict(self) -> Dict[str, Any]:
        """
        Return a dict of the config
        """
        return_dict = dict()
        for k, v in self.conf_data.items():
            return_dict[k] = self.flatten_recursive(v)
        return return_dict
