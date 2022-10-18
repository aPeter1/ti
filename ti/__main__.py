import argparse
import logging

from handlers import *


class Commands:
    LOG = "log"
    CONFIG = "config"
    OUT = "out"
    MARK = 'mark'
    UNMARK = 'unmark'
    DELETE = 'del'


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(prog='ti')
    arg_parser.add_argument("-v", action="store_true", dest="verbose")

    base_subparser = argparse.ArgumentParser(add_help=False)
    base_subparser.add_argument("-v", action="store_true", dest="verbose", help="Enable verbose logging")

    subparsers = arg_parser.add_subparsers(dest='command')

    arg_parser_config = subparsers.add_parser(Commands.CONFIG, help='Set the config file', parents=[base_subparser])
    arg_parser_config.add_argument('file', type=str, help='Path of the configuration file')

    arg_parser_message = subparsers.add_parser(Commands.LOG, help='Log a message', parents=[base_subparser])
    arg_parser_message.add_argument('type', type=str, help='The type of message to log')
    arg_parser_message.add_argument('message', type=str, help='The message to log')

    arg_parser_print = subparsers.add_parser(Commands.OUT, help='Output all messages of type', parents=[base_subparser])
    arg_parser_print.add_argument('type', type=str, nargs='+', help='The type of message to output')
    arg_parser_print.add_argument('-s', action='store_true', dest='simple', help='Only output messages')

    arg_parser_mark = subparsers.add_parser(Commands.MARK, help='Mark message(s) at index(s)', parents=[base_subparser])
    arg_parser_mark.add_argument('type', type=str, help='The type of message to mark')
    arg_parser_mark.add_argument('range', type=int, nargs='+', help='Index to mark or two to indicate a range')

    arg_parser_unmark = subparsers.add_parser(Commands.UNMARK, help='Unmark message(s) at index(s)', parents=[base_subparser])
    arg_parser_unmark.add_argument('type', type=str, help='The type of message to unmark')
    arg_parser_unmark.add_argument('range', type=int, nargs='+', help='Index to unmark or two to indicate a range')

    arg_parser_delete = subparsers.add_parser(Commands.DELETE, help='Delete message(s) at index(s)', parents=[base_subparser])
    arg_parser_delete.add_argument('type', type=str, help='The type of message to delete')
    arg_parser_delete.add_argument('range', type=int, nargs='+', help='Index to delete or two to indicate a range')

    arg_namespace = arg_parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if arg_namespace.verbose else logging.INFO, format='%(message)s')

    try:
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
            handle_del(arg_namespace)
    except Exception as e:
        log_error("An unknown exception occurred", e)

