from gallop.config import BaseConfig

config = BaseConfig(a=1)


def test_config_set_get():
    assert config.a == 1
    config.a = 2
    assert config["a"] == 2
    config['a'] = 3
    assert config.a == 3


config["b"] = 4
config.c = {"hello": "here"}


def test_another_key():
    assert config.b == 4
    assert len(config) == 3


def test_save_load():
    config.to_json("test/test.json")
    config.to_yaml("test/test.yaml")
    config2 = BaseConfig.from_json("test/test.json")
    config3 = BaseConfig.from_yaml("test/test.yaml")
    assert config2.a == config3.a == 3
    assert config2.b == config3.b == 4
    assert len(config2) == len(config3) == 3


def test_iteration():
    for k in config:
        assert k in "abc"
    for key in config.keys():
        assert key in "abc"
    for key, value in config.items():
        assert key in "abc"
        assert config[key] == value


def test_inheritance():
    class Config(BaseConfig):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.d = 5

    config = Config(a=1)
    assert config.d == 5
    assert config.a == 1
    assert len(config) == 2
    config.to_json("test/test2.json")
    config.to_yaml("test/test2.yaml")
    config2 = Config.from_json("test/test2.json")
    config3 = Config.from_yaml("test/test2.yaml")
    assert config2.a == config3.a == 1
    assert config2.d == config3.d == 5
    assert len(config2) == len(config3) == 2


def test_recursive():
    """
    Test the recursiveness of the BaseConfig class
    """
    config = BaseConfig(a=1, b=2, c={"hello": "here"})
    assert config.c.hello == "here"
    config.c.hello = "there"
    assert config.c.hello == "there"
    config.c.hello = {"world": "here"}
    assert config.c.hello.world == "here"

    config.to_json("test/test3.json")
    config.to_yaml("test/test3.yaml")
    config2 = BaseConfig.from_json("test/test3.json")
    config3 = BaseConfig.from_yaml("test/test3.yaml")
    assert config2.a == config3.a == 1
    assert config2.b == config3.b == 2
    assert config2.c.hello.world == config3.c.hello.world == "here"
    assert len(config2) == len(config3) == 3
