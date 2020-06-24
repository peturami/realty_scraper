import yaml
import os
from typing import Dict, Any


def get_folder_path(folder: str) -> str:
    dirname = os.path.dirname(os.path.normpath(__file__))
    return os.path.join(dirname, os.pardir, folder)

def init_config(folder: str, filename: str) -> Dict[str, Any]:
    config_file = os.path.join(get_folder_path(folder), filename)
    with open(config_file, "r", encoding='utf8') as yamlfile:
        cfg = yaml.safe_load(yamlfile)
    return cfg
