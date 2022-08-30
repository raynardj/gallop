from typing import Any, Dict
import json
import yaml


class BaseConfig:
    """
    The base configuration class for gallop application
    """
    def __init__(self, **kwargs):
        super().__setattr__("conf_data", kwargs)

    def __getattr__(self, key: str):
        conf_data = self.__getattribute__("conf_data")
        if key in conf_data:
            return conf_data[key]
        else:
            return super().__getattribute__(key)

    def __hasattr__(self, key: str):
        return super().__hasattr__(key)

    def __setattr__(self, key: str, value: Any):
        conf_data = self.__getattribute__("conf_data")
        conf_data[key] = value

    def __getitem__(self, key: str):
        if key not in self.conf_data:
            raise KeyError(f"Config has no key {key}")
        return self.conf_data[key]

    def __setitem__(self, key: str, value: Any):
        self.conf_data[key] = value

    def __contains__(self, key: str):
        return key in self.conf_data

    def __repr__(self) -> str:
        return f"Config({self.conf_data})"

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
            json.dump(self.conf_data, f)

    def to_yaml(self, path: str):
        with open(path, "w") as f:
            yaml.safe_dump(self.conf_data, f)

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
