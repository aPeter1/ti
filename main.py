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
    OUT = "out"
    MARK = 'mark'
    UNMARK = 'unmark'
    DELETE = 'del'


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


def get_user_config():
    ti_config = get_ti_config()
    if ti_config[TiConfigKeys.USER_CONFIG] is None:
        raise Exception("Configuration file has not been set yet.")

    user_config_file = ti_config[TiConfigKeys.USER_CONFIG]
    if not os.path.isfile(user_config_file):
        raise FileNotFoundError(f"Configuration file '{user_config_file}' does not exist.")

    verify_user_config(user_config_file)
    user_config = parse_config(user_config_file)

    return user_config


def get_user_type_path(namespace, user_config):
    if namespace.type not in user_config:
        raise Exception(f"Type '{namespace.type}' not found in user configuration.")

    def get_path_recursive(type_name):
        type_value = user_config[type_name]
        if type_value in user_config:
            return get_path_recursive(type_value)
        return type_value

    return get_path_recursive(namespace.type)


def handle_log(namespace):
    user_config = get_user_config()
    log_path = get_user_type_path(namespace, user_config)

    if not os.path.isfile(log_path):
        try:
            attempt_to_create_file(log_path)
        except Exception:
            raise Exception(f"Log file path '{log_path}' was invalid.")

    with open(log_path, 'a') as fp:
        fp.write(f"{namespace.type}|||0|||{namespace.message}\n")


def handle_out(namespace):
    user_config = get_user_config()
    log_path = get_user_type_path(namespace, user_config)

    if not os.path.isfile(log_path):
        try:
            attempt_to_create_file(log_path)
        except Exception:
            raise Exception(f"Log file path '{log_path}' was invalid.")

    with open(log_path, 'r') as fp:
        n = 0
        for i, line in enumerate(fp.readlines()):
            if i == 0 and line[0] == '#':
                continue

            message_type, marked, message = line.split('|||')
            if message_type != namespace.type:
                continue

            n += 1
            message = message.strip('\n')
            print(f"[{n}][{' ' if marked == '0' else 'X'}] {message}")


def handle_mark(namespace, mark):
    user_config = get_user_config()
    log_path = get_user_type_path(namespace, user_config)

    if not os.path.isfile(log_path):
        try:
            attempt_to_create_file(log_path)
            return
        except Exception:
            raise Exception(f"Log file path '{log_path}' was invalid.")

    if len(namespace.range) > 2:
        raise Exception(f"{namespace.range} values given for range, expected 1 or 2.")

    lower = min(namespace.range)
    upper = max(namespace.range)
    single = lower == upper

    with open(log_path, 'r') as fp:
        n = 0
        lines = fp.readlines()
        for i, line in enumerate(lines):
            if i == 0 and line[0] == '#':
                continue

            message_type, marked, message = line.split('|||')
            if message_type != namespace.type:
                continue

            n += 1
            if (single and n == lower) or lower <= n <= upper:
                message = message.strip('\n')
                lines[i] = f"{message_type}|||{1 if mark else 0}|||{message}\n"

    with open(log_path, 'w') as fp:
        fp.writelines(lines)

    handle_out(namespace)


def handle_delete(namespace):
    user_config = get_user_config()
    log_path = get_user_type_path(namespace, user_config)

    if not os.path.isfile(log_path):
        try:
            attempt_to_create_file(log_path)
            return
        except Exception:
            raise Exception(f"Log file path '{log_path}' was invalid.")

    if len(namespace.range) > 2:
        raise Exception(f"{namespace.range} values given for range, expected 1 or 2.")

    lower = min(namespace.range)
    upper = max(namespace.range)
    single = lower == upper

    with open(log_path, 'r') as fp:
        n = 0
        lines = fp.readlines()
        removed = 0
        for i, line in enumerate(lines.copy()):
            if i == 0 and line[0] == '#':
                continue

            message_type, marked, message = line.split('|||')
            if message_type != namespace.type:
                continue

            n += 1
            if (single and n == lower) or lower <= n <= upper:
                del lines[i - removed]
                removed += 1

    with open(log_path, 'w') as fp:
        fp.writelines(lines)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(prog='ti')
    subparsers = arg_parser.add_subparsers(dest='command')

    arg_parser_config = subparsers.add_parser(Commands.CONFIG, help='Set the configuration file')
    arg_parser_config.add_argument('file', type=str, help='Path of the configuration file')

    arg_parser_message = subparsers.add_parser(Commands.LOG, help='Log a message')
    arg_parser_message.add_argument('type', type=str, help='The type of message to log')
    arg_parser_message.add_argument('message', type=str, help='The message to log')

    arg_parser_print = subparsers.add_parser(Commands.OUT, help='Output all messages of type')
    arg_parser_print.add_argument('type', type=str, help='The type of message to output')

    arg_parser_mark = subparsers.add_parser(Commands.MARK, help='Mark message(s) at index(s)')
    arg_parser_mark.add_argument('type', type=str, help='The type of message to mark')
    arg_parser_mark.add_argument('range', type=int, nargs='+', help='Index to mark or two to indicate a range')

    arg_parser_unmark = subparsers.add_parser(Commands.UNMARK, help='Unmark message(s) at index(s)')
    arg_parser_unmark.add_argument('type', type=str, help='The type of message to unmark')
    arg_parser_unmark.add_argument('range', type=int, nargs='+', help='Index to unmark or two to indicate a range')

    arg_parser_delete = subparsers.add_parser(Commands.DELETE, help='Delete message(s) at index(s)')
    arg_parser_delete.add_argument('type', type=str, help='The type of message to delete')
    arg_parser_delete.add_argument('range', type=int, nargs='+', help='Index to delete or two to indicate a range')

    arg_namespace = arg_parser.parse_args()

    if arg_namespace.command == Commands.LOG:
        handle_log(arg_namespace)
    elif arg_namespace.command == Commands.CONFIG:
        handle_config(arg_namespace)
    elif arg_namespace.command == Commands.OUT:
        handle_out(arg_namespace)
    elif arg_namespace.command == Commands.MARK:
        handle_mark(arg_namespace, True)
    elif arg_namespace.command == Commands.UNMARK:
        handle_mark(arg_namespace, False)
    elif arg_namespace.command == Commands.DELETE:
        handle_delete(arg_namespace)
    else:
        raise ValueError(f"Invalid command '{arg_namespace.command}'")



