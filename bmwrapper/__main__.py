#!/usr/bin/python2.7

import argparse
import asyncore
import threading
import sys
import logging

import outgoing
import incoming


def configure_logging(log_level):
    numeric_level = getattr(logging, log_level.upper(), None)
    logging.basicConfig(format='%(asctime)s %(levelname)s - %(message)s', level=numeric_level)


def run(arguments):
    run_event = threading.Event()
    run_event.set()
    logging.info("Starting SMTP server at {0}:{1}".format(arguments.smtp_host, arguments.smtp_port))
    outserv = outgoing.outgoingServer((arguments.smtp_host, arguments.smtp_port), None)

    logging.info("Starting POP server at {0}:{1}".format(arguments.pop_host, arguments.pop_port))
    inserv = incoming.incomingServer(arguments.pop_host, arguments.pop_port, run_event)

    try:
        logging.info("Press Ctrl+C to exit.")
        asyncore.loop()
    except KeyboardInterrupt:
        logging.info("Exiting...")
        run_event.clear()
        logging.debug("waiting for threads...")
        inserv.join()
        logging.debug("all threads done...")
        sys.exit(0)


def usage():
    return """

    bmwrapper [options]

    EXAMPLES
    bmwrapper -l info -p 12344 -s 12345
    bmwrapper --log-level info --pop-port 12344 --smtp-port 12345

    OPTIONS
    -l, --log-level <level>
        Expected values are: DEBUG, INFO, WARNING, ERROR, CRITICAL

    -p, --pop-port <number>
        Port that the POP server should listen to

    -s, --smtp-port <number>
        Port that the SMTP server should listen to
"""


def arg_to_key(arg):
    """
    Convert a long-form command line switch to an equivalent dict key,
    Example: arg_to_key('--super-flag') == 'super_flag'
    """
    return arg.lstrip('-').replace('-', '_')


def configure_parser(parser):
    defaults = {
        'bm_host': '',
        'bm_pass': '',
        'bm_port': 8442,
        'bm_user': '',
        'log_level': 'info',
        'pop_host': '0.0.0.0',
        'pop_port': 12344,
        'smtp_host': '0.0.0.0',
        'smtp_port': 12345
    }

    plain_args = (
        ('--bm-host',),
        ('--bm-pass',),
        ('--bm-user',),
        ('--log-level', '-l'),
        ('--smtp-host',),
        ('--pop-host',),
    )
    for switches in plain_args:
        key = arg_to_key(switches[0])
        parser.add_argument(*switches, default=defaults[key])

    int_args = (
        ('--bm-port',),
        ('--pop-port', '-p'),
        ('--smtp-port', '-s'),
    )
    for switches in int_args:
        key = arg_to_key(switches[0])
        parser.add_argument(*switches, type=int, default=defaults[key])

    return parser


def main():
    parser = configure_parser(argparse.ArgumentParser(
        description='bmwrapper',
        usage=usage(),
        add_help=False
    ))
    arguments = parser.parse_args()

    configure_logging(arguments.log_level)
    run(arguments)

if __name__ == '__main__':
    main()
