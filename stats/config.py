import yaml

def read_file(file_path):
    """
    Read a given yaml
    :param file_path: path of yaml file
    :return: yaml data as a python dictionary
    """
    try:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
        return data
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return None


config = read_file('config.yaml')


