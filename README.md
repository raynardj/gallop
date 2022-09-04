# gallop
🐎 New level of python develop. Source code from [github](https://github.com/raynardj/gallop)

> More dynamic in design, more configuration driven

[![PyPI version](https://img.shields.io/pypi/v/gallop)](https://pypi.org/project/gallop/)
![License](https://img.shields.io/github/license/raynardj/forgebox)
[![Test](https://github.com/raynardj/gallop/actions/workflows/test.yml/badge.svg)](https://github.com/raynardj/gallop/actions/workflows/test.yml)
[![pypi build](https://github.com/raynardj/gallop/actions/workflows/publish.yml/badge.svg)](https://github.com/raynardj/gallop/actions/workflows/publish.yml)

```
   [-;-/=_
    `-; \=_       ___        _________    __    __    ____  ____ 
      ) ,"-...--./===--__   / ____/   |  / /   / /   / __ \/ __ \ 
    __|/      /  ]`        / / __/ /| | / /   / /   / / / / /_/ /
   /;--> >...-\ <\_       / /_/ / ___ |/ /___/ /___/ /_/ / ____/ 
   `- <<,      7/-.\,     \____/_/  |_/_____/_____/\____/_/      
       `-     /(   `-     
```

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

## Run python task from config
You can turn any callable execution in to configuration, eg save the following
```yaml
func_name: use:print
args:
  - "hello world"
```

to `sometask.yaml` and run `gallop sometask`

Is the same to run the python script
```python
print("hello world")
```

### `param:` configuration
We can change the value on the run, while pointing to the position in the config, using a chain of keys (keys to dict or list).

eg. to change the key `args`, of its 1st element, we can run
```shell
gallop sometask --param:args.0 changed_world
```

## Advanced usage
### Some simple grammar
* `checkin: somekey`, save the result to a centralized dictionary with key `somekey`
* `checkout: somekey`, use the result from the centralized dictionary with key `somekey`
* `checkout: env:DATA_HOME`, use the result from the environment variable `DATA_HOME`
* `use:some.module`, use or import the module `some.module` as the callable, eg
    * `func_name: use:os.path.join`, use the function `os.path.join`
    * `func_name: use:pandas.DataFrame`, use the class `pandas.DataFrame`

### Examples
#### Inference BERT model
> If you have `transformers` installed, you can run the following example directly to featurize a sentence

```yaml
pred_task:
  - func_name: use:transformers.AutoModel.from_pretrained
    args:
      - bert-base-uncased
    checkin: model
    description: |
      Load pretrained model
  - func_name: use:transformers.AutoTokenizer.from_pretrained
    args:
      - bert-base-uncased
    checkin: tokenizer
    description: |
      Load pretrained tokenizer
  - func_name: tokenizer
    args:
      - - "Hello, the capital of [MASK] is Paris"
    kwargs:
      return_tensors: pt
      max_length: 128
      truncation: True
      padding: True
    checkin: inputs
  - func_name: use:logging.warning
    args:
      - func_name: model
        kwargs:
          input_ids:
            checkout: inputs.input_ids
          attention_mask:
            checkout: inputs.attention_mask
        checkin: features
```

This equals to the following `python` script
```python
import logging
from transformers import AutoModel, AutoTokenizer

model = AutoModel.from_pretrained("bert-base-uncased")
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
inputs = tokenizer(
    "Hello, the capital of [MASK] is Paris",
    return_tensors="pt",
    max_length=128,
    truncation=True,
    padding=True,
)
logging.warning(model(
    input_ids=inputs.input_ids,
    attention_mask=inputs.attention_mask,
))
```

Save the yaml to `run_bert.yaml` and you can use `gallop run_bert --output features` to run the task.

Run in commandline with changed value, and printout one of the checkout value
```shell

```

And run it with changed value
```
gallop test/test_transformers --loglevel debug --output features \
    --param:pred_task.2.args.0.0 "The [MASK] house is where the POTUS live and work"   
```


## Related project
> From the same lead author
* Python [category](https://github.com/raynardj/category) management accelerated with Rust
* Data science basic toolset [forgebox](https://github.com/raynardj/forgebox)