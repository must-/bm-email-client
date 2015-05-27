#!/usr/bin/python2.7

import asyncore
import threading
import sys
import logging

import outgoing
import incoming


loglevel = 'debug'
smtp_host = 'localhost'
smtp_port = 12345
pop_host = 'localhost'
pop_port = 12344


def configure_logging():
    numeric_level = getattr(logging, loglevel.upper(), None)
    logging.basicConfig(format='%(asctime)s %(levelname)s - %(message)s', level=numeric_level)

def run():
    configure_logging()

    run_event = threading.Event()
    run_event.set()
    logging.info("Starting SMTP server at {0}:{1}".format(smtp_host, smtp_port))
    outserv = outgoing.outgoingServer((smtp_host, smtp_port), None)

    logging.info("Starting POP server at {0}:{1}".format(pop_host, pop_port))
    inserv = incoming.incomingServer(pop_host, pop_port, run_event)

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

if __name__ == '__main__':
    run()
