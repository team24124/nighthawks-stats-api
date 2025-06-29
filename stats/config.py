import yaml
from pathlib import Path

def read_file(file_path):
    """
    Read a given yaml
    :param file_path: path of yaml file
    :return: yaml data as a python dictionary
    """

    script_dir = Path(__file__).resolve().parent
    target_file_path = script_dir / file_path
    try:
        with open(target_file_path, 'r') as file:
            data = yaml.safe_load(file)
        return data
    except FileNotFoundError:
        print(f"Error: File not found at {target_file_path}")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return None


config = read_file('config.yaml')


