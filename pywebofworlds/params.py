import os

import astropy.io.misc.yaml as yaml

import pywebofworlds.utils as u

home_path = os.path.expanduser("~")
config_dir = os.path.join(home_path, ".pywebofworlds")
config_file = os.path.join(config_dir, "config.yaml")

config_default = {
    "data_dir": os.path.join(home_path, "pywebofworlds")
}


def check_for_config():
    u.mkdir_check(config_dir)
    config_dict = load_params(config_file)
    if config_dict is None:
        save_params(config_file, config_default)
        print(f"No config file was detected at {config_file}.")
        print(f"A fresh config file has been created at '{config_file}'")
        print(
            "In this file, please set 'top_data_dir' to a valid path in which to store all "
            "data products of this package (This may require a large amount of space.).")
        print("You may also like to specify an alternate param_dir")
        config_dict = load_params(config_file)
    return config_dict


def get_project_path():
    return os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))


def load_params(file: str):
    file = u.sanitise_file_ext(file, '.yaml')
    file = check_abs_path(file)
    print('Loading parameter file from ' + str(file))

    if os.path.isfile(file):
        with open(file) as f:
            p = yaml.load(f)
    else:
        p = None
        print('No parameter file found at', str(file) + ', returning None.')
    return p


def save_params(file: str, dictionary: dict):
    file = u.sanitise_file_ext(path=file, ext=".yaml")
    file = check_abs_path(file)

    print('Saving parameter file to ' + str(file))

    with open(file, 'w') as f:
        yaml.dump(dictionary, f)


def check_abs_path(path: str):
    if not os.path.isabs(path):
        path = os.path.join(data_dir, path)
    return path


config = check_for_config()
project_dir = get_project_path()
data_dir_project = os.path.join(project_dir, "pywebofworlds", "data")
data_dir = config['data_dir']
u.mkdir_check(data_dir)


def data_subdir(obj_type: str, category: str = None, absolute: bool = False):
    if category is None:
        category = obj_type
    path = os.path.join(category, obj_type)
    if absolute:
        path = os.path.join(data_dir, path)
    return path


def registry_path(obj_type: str, category: str = None):
    return os.path.join(
        data_subdir(obj_type=obj_type, category=category),
        f"{obj_type}_registry.yaml"
    )


def load_registry(obj_type: str, category: str = None):
    path = registry_path(obj_type=obj_type, category=category)
    if os.path.isfile(path):
        return load_params(path)
    else:
        return {}


def save_registry(obj_type: str, registry: dict, category: str = None):
    path = registry_path(obj_type=obj_type, category=category)
    if os.path.isfile(path):
        save_params(file=path, dictionary=registry)
    else:
        u.mkdir_check_nested(path, remove_last=True)
        save_params(path, registry)


def update_registry(obj_type: str, category: str = None, registry: dict = None):
    if registry is None:
        registry = load_registry(obj_type=obj_type, category=category)
    subdir = data_subdir(obj_type=obj_type, category=category)
    for file in filter(lambda f: f.endswith(".yaml") or file.endswith(".yml"), os.listdir(subdir)):
        identifier = file.split(".")[0]
        if not identifier.endswith("_registry"):
            registry[identifier] = os.path.join(subdir, file)
    return registry



