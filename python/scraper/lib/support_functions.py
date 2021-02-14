import yaml
import os
from typing import Dict, Any


def get_path(*folder: str) -> str:
    dirname = os.path.dirname(os.path.normpath(__file__))
    return os.path.join(dirname, os.pardir, os.pardir, os.pardir, *folder)

def init_config(filepath: str) -> Dict[str, Any]:
    with open(filepath, "r", encoding='utf8') as yamlfile:
        cfg = yaml.safe_load(yamlfile)
    return cfg

def running_script_name(script):
    return script.split(".")[-1]
