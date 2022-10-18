import os
import logging

import util


__base_config_path = '.ticonfig.json'
__logger = logging.getLogger("TI")


def log_error(message, e):
    __logger.debug("Exception", exc_info=e)
    __logger.warning(f"{message} (see more with verbose [-v])")


def handle_config(namespace):
    # Verify user configuration is valid
    try:
        user_config = util.retrieve_user_config(namespace.file)
        util.verify_user_config(user_config)
    except Exception as e:
        log_error("Your configuration file is improperly formatted", e)
        return

    # Update the TI configuration file
    try:
        ti_config = util.retrieve_ti_config(__base_config_path)
        ti_config[util.TiConfigKeys.USER_CONFIG] = os.path.abspath(namespace.file)
        util.write_config(__base_config_path, ti_config)
    except Exception as e:
        log_error("An error occurred updating the TI configuration", e)
        return

    __logger.info('Saved user configuration file. You are ready to use TI!')


def handle_log(namespace):
    # Verify user configuration is valid
    try:
        user_config = util.retrieve_user_config_from_ti_config(__base_config_path)
        util.verify_user_config(user_config)
    except Exception as e:
        log_error("Your configuration file is improperly formatted or has not been specified", e)
        return

    # Get the log path for the type
    try:
        log_path = util.get_user_type_path(namespace.type, user_config)
    except Exception as e:
        log_error(f"Could not determine log path for {namespace.type}. Check your config", e)
        return

    # Write the message to the log file
    try:
        if not os.path.isfile(log_path):
            util.write_file(log_path, ["# TI LOG\n"])

        message = util.format_message(namespace.type, 0, namespace.message)
        util.write_file(log_path, [message], 'a')
    except Exception as e:
        log_error("An error occurred while writing to log file. Check your config", e)
        return


def handle_out(namespace):
    # Verify user configuration is valid
    try:
        user_config = util.retrieve_user_config_from_ti_config(__base_config_path)
        util.verify_user_config(user_config)
    except Exception as e:
        log_error("Your configuration file is improperly formatted or has not been specified", e)
        return

    # Iterate through provided types
    for message_type in namespace.type:
        if not namespace.simple:
            __logger.info(f"### Messages for {message_type} ###")

        try:
            log_path = util.get_user_type_path(message_type, user_config)
        except Exception as e:
            log_error(f"Could not determine log path for {message_type}. Check your config", e)
            return

        if not os.path.isfile(log_path):
            __logger.info(f"No messages made yet for {message_type}")
            continue

        with open(log_path, 'r') as fp:
            n = 0
            for i, line in enumerate(fp.readlines()):
                if i == 0 and line[0] == '#':
                    continue

                try:
                    line_message_type, marked, message = line.split('|||')
                except Exception as e:
                    log_error(f"Log in file {log_path} was improperly formatted", e)
                    continue

                if line_message_type == message_type:
                    n += 1
                    message = message.strip('\n')
                    if namespace.simple:
                        __logger.info(message)
                    else:
                        __logger.info(f"[{n}][{' ' if marked == '0' else 'X'}] {message}")


def handle_mark(namespace, mark):
    # Verify user configuration is valid
    try:
        user_config = util.retrieve_user_config_from_ti_config(__base_config_path)
        util.verify_user_config(user_config)
    except Exception as e:
        log_error("Your configuration file is improperly formatted or has not been specified", e)
        return

    try:
        log_path = util.get_user_type_path(namespace.type, user_config)
    except Exception as e:
        log_error(f"Could not determine log path for {namespace.type}. Check your config", e)
        return

    if len(namespace.range) > 2:
        __logger.warning("Expect one or two arguments to specify range of messages to mark")
        return

    lower = min(namespace.range)
    upper = max(namespace.range)
    single = lower == upper

    with open(log_path, 'r') as fp:
        n = 0
        lines = fp.readlines()
        for i, line in enumerate(lines):
            if i == 0 and line[0] == '#':
                continue

            try:
                message_type, marked, message = line.split('|||')
            except Exception as e:
                log_error(f"Log in file {log_path} was improperly formatted", e)
                continue

            if message_type != namespace.type:
                continue

            n += 1
            if (single and n == lower) or lower <= n <= upper:
                message = message.strip('\n')
                lines[i] = f"{message_type}|||{1 if mark else 0}|||{message}\n"

    util.write_file(log_path, lines)


def handle_del(namespace):
    # Verify user configuration is valid
    try:
        user_config = util.retrieve_user_config_from_ti_config(__base_config_path)
        util.verify_user_config(user_config)
    except Exception as e:
        log_error("Your configuration file is improperly formatted or has not been specified", e)
        return

    try:
        log_path = util.get_user_type_path(namespace.type, user_config)
    except Exception as e:
        log_error(f"Could not determine log path for {namespace.type}. Check your config", e)
        return

    if len(namespace.range) > 2:
        __logger.warning("Expect one or two arguments to specify range of messages to mark")
        return

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

            try:
                message_type, marked, message = line.split('|||')
            except Exception as e:
                log_error(f"Log in file {log_path} was improperly formatted", e)
                continue

            if message_type != namespace.type:
                continue

            n += 1
            if (single and n == lower) or lower <= n <= upper:
                del lines[i - removed]
                removed += 1

    util.write_file(log_path, lines)
