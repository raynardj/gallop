# gallop
🐎 New level of python develop. Source code from [github](https://github.com/raynardj/gallop)

> More dynamic in design, more configuration driven

[![PyPI version](https://img.shields.io/pypi/v/gallop)](https://pypi.org/project/gallop/)
![License](https://img.shields.io/github/license/raynardj/forgebox)
[![Test](https://github.com/raynardj/gallop/actions/workflows/test.yml/badge.svg)](https://github.com/raynardj/gallop/actions/workflows/test.yml)
[![pypi build](https://github.com/raynardj/gallop/actions/workflows/publish.yml/badge.svg)](https://github.com/raynardj/gallop/actions/workflows/publish.yml)

## Install
```shell
pip install gallop
```

## Configuration Management
```python
from gallop.config import BaseConfig

config = BaseConfig(a=1)
config.a = 2
config.b = 3

config.to_json("some/path.json")
config.to_yaml("some/path.yaml")
```
## Related project
> From the same lead author
* Python [category](https://github.com/raynardj/category) management accelerated with Rust
* Data science basic toolset [forgebox](https://github.com/raynardj/forgebox)