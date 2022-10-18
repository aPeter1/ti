import sys
import enum
import argparse
import json
import os

__base_config_path = '.ticonfig.json'


class TiConfigKeys:
    USER_CONFIG = "user_config"

class UserConfigKeys:
    DEFAULT = "default"


class Commands:
    LOG = "log"
    CONFIG = "config"


def parse_config(path_to_json_file: str) -> dict:
    with open(path_to_json_file, 'r') as fp:
        return json.load(fp)


def create_ti_config():
    base_config = {
        "user_config": None
    }

    with open(__base_config_path, 'w') as fp:
        json.dump(base_config, fp)


def get_ti_config():
    if not os.path.exists(__base_config_path):
        print("Setting up ti configuration ...")
        create_ti_config()

    config = parse_config(__base_config_path)
    if TiConfigKeys.USER_CONFIG not in config:
        config[TiConfigKeys.USER_CONFIG] = None

    return config


def attempt_to_create_file(file_path):
    with open(file_path, 'w') as fp:
        fp.write("# TI LOG\n")


def verify_user_config(file_path):
    try:
        user_config = parse_config(file_path)
    except Exception as e:
        raise Exception("Configuration file was improperly formatted. See inner exception") from e

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
                attempt_to_create_file(v)
            except Exception as e:
                raise Exception(f"Value for user configuration key '{k}' was not a "
                                f"valid section name or file path.") from e
        user_config[k] = os.path.abspath(v)

    with open(file_path, 'w') as fp:
        json.dump(user_config, fp)


def handle_config(namespace):
    if not os.path.isfile(namespace.file):
        raise FileNotFoundError(f"Configuration file '{namespace.file}' does not exist.")

    verify_user_config(namespace.file)

    ti_config = get_ti_config()
    ti_config[TiConfigKeys.USER_CONFIG] = os.path.abspath(namespace.file)

    with open(__base_config_path, 'w') as fp:
        json.dump(ti_config, fp)

    print('Saved user configuration file. You are ready to use TI!')


def handle_log(namespace):
    ti_config = get_ti_config()
    if ti_config[TiConfigKeys.USER_CONFIG] is None:
        raise Exception("Configuration file has not been set yet.")

    user_config_file = ti_config[TiConfigKeys.USER_CONFIG]
    if not os.path.isfile(user_config_file):
        raise FileNotFoundError(f"Configuration file '{user_config_file}' does not exist.")

    verify_user_config(user_config_file)
    user_config = parse_config(user_config_file)

    if namespace.type not in user_config:
        raise Exception(f"Type '{namespace.type}' not found in user configuration.")

    def get_path_recursive(type_name):
        type_value = user_config[type_name]
        if type_value in user_config:
            return get_path_recursive(type_value)
        return type_value

    log_path = get_path_recursive(namespace.type)
    if not os.path.isfile(log_path):
        try:
            attempt_to_create_file(log_path)
        except Exception:
            raise Exception(f"Log file path '{log_path}' was invalid.")

    with open(log_path, 'a') as fp:
        fp.write(namespace.message + "\n")


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(prog='ti')
    subparsers = arg_parser.add_subparsers(dest='command')

    arg_parser_config = subparsers.add_parser('config', help='Set the configuration file')
    arg_parser_config.add_argument('file', type=str, help='Path of the configuration file')

    arg_parser_message = subparsers.add_parser('log', help='Log a message')
    arg_parser_message.add_argument('type', type=str, help='The type of message to log')
    arg_parser_message.add_argument('message', type=str, help='The message to log')

    arg_namespace = arg_parser.parse_args()

    if arg_namespace.command == Commands.LOG:
        handle_log(arg_namespace)
    elif arg_namespace.command == Commands.CONFIG:
        handle_config(arg_namespace)
    else:
        raise ValueError(f"Invalid command '{arg_namespace.command}'. This branch is unreachable so congratulations!")



