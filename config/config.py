import yaml

with open("config/config.yaml", "r") as f:
    _config = yaml.safe_load(f)


def get_config():
    return _config
