#!/usr/bin/python2.7

import argparse
import asyncore
import threading
import sys
import logging

import outgoing
import incoming


def configure_logging(loglevel):
    numeric_level = getattr(logging, loglevel.upper(), None)
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
bm-email-client [options]

    EXAMPLES
    bm-email-client -l info -p 12344 -s 12345
    bm-email-client --log-level info --pop-port 12344 --smtp-port 12345

    OPTIONS
    -l, --log-level <level>
        Expected values are: DEBUG, INFO, WARNING, ERROR, CRITICAL

    -p, --pop-port <number>
        Port that the POP server should listen to

    -s, --smtp-port <number>
        Port that the SMTP server should listen to
"""


def configure_parser(parser):
    return parser;


def main():
    parser = configure_parser(argparse.ArgumentParser(
        description='BM-email-client',
        usage=usage(),
        add_help=False
    ))

    arguments = parser.parse_args()
    arguments.loglevel = 'debug'
    arguments.smtp_host = 'localhost'
    arguments.smtp_port = 12345
    arguments.pop_host = 'localhost'
    arguments.pop_port = 12344

    configure_logging(arguments.loglevel)
    run(arguments)


if __name__ == '__main__':
    main()
