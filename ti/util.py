import json
import os
import logging


__logger = logging.getLogger("TI")


class TiConfigKeys:
    USER_CONFIG = "user_config"


class UserConfigKeys:
    DEFAULT = "default"


def format_message(message_type, marked, message):
    return f"{message_type}|||{1 if marked else 0}|||{message}\n"


def parse_config(file_path: str) -> dict:
    with open(file_path, 'r') as fp:
        return json.load(fp)


def write_config(file_path: str, config: dict) -> None:
    with open(file_path, 'w') as fp:
        json.dump(config, fp)


def write_file(file_path: str, contents: list[str] = None, write_mode: str = 'w') -> None:
    with open(file_path, write_mode) as fp:
        if contents is not None:
            fp.writelines(contents)


def retrieve_ti_config(file_path):
    if not os.path.isfile(file_path):
        write_config(file_path, {TiConfigKeys.USER_CONFIG: None})

    return parse_config(file_path)


def verify_user_config(user_config):
    if len(user_config) == 0:
        raise Exception("Configuration file is empty.")

    if UserConfigKeys.DEFAULT not in user_config.keys():
        raise Exception("Configuration file does not set default.")

    for k, v in user_config.items():
        if v in user_config and v != k:
            continue
        elif not isinstance(v, str):
            raise Exception(f"Value for user configuration key '{k}' must be a string. Instead got '{v}'")
        elif not os.path.isfile(v):
            try:
                write_file(v, ["# TI CONFIG"])
            except Exception as e:
                raise Exception(f"Value for user configuration key '{k}' was not a "
                                f"valid section name or file path.") from e


def retrieve_user_config(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Configuration file '{file_path}' does not exist.")

    try:
        user_config = parse_config(file_path)
    except Exception as e:
        raise Exception("Configuration file was improperly formatted. See inner exception") from e

    return user_config


def retrieve_user_config_from_ti_config(file_path):
    ti_config = retrieve_ti_config(file_path)

    if TiConfigKeys.USER_CONFIG not in ti_config:
        write_config(file_path, {TiConfigKeys.USER_CONFIG: None})
        raise Exception("User config has not been specified")

    user_config_path = ti_config[TiConfigKeys.USER_CONFIG]
    if user_config_path is None:
        raise Exception("User config has not been specified")

    return retrieve_user_config(user_config_path)


def get_user_type_path(namespace_type_name, user_config):
    if namespace_type_name not in user_config:
        raise Exception(f"Type '{namespace_type_name}' not found in user configuration.")

    def get_path_recursive(type_name, depth):
        if depth > len(user_config):
            raise Exception(f"The user configuration contains a circular dependency, can't determine log path")

        type_value = user_config[type_name]
        if type_value in user_config:
            return get_path_recursive(type_value, depth + 1)
        return type_value

    return get_path_recursive(namespace_type_name, 0)
