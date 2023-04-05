import json
import logging.config
import sys

# set the default encoding to UTF-8
sys.stdout.reconfigure(encoding="utf-8")

with open("config/log_config.json", "rt") as f:
    config = json.load(f)

logging.config.dictConfig(config)

logger = logging.getLogger("logger")
