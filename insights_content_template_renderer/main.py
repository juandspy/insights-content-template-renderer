"""
Contains insights_content_template_renderer initialization and command line handler.
"""

import logging
import sys
import os
import json
import argparse
from pathlib import Path
import pkg_resources
from gunicorn.app import base
from gunicorn import glogging
from insights_content_template_renderer.endpoints import app

log = logging.getLogger(__name__)


def is_valid_config(parser, arg):
    """Parses JSON configuration file to dictionary"""
    conf = {}
    if not os.path.exists(arg):
        parser.error(f"The file {arg} does not exist!")
    else:
        with open(arg, 'r', encoding='UTF-8') as config_file:
            conf = json.load(config_file)
    return conf


def parse_args():
    """Parse the command line options and arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Application Configuration.",
                        type=lambda x: is_valid_config(parser, x))
    parser.add_argument("--version", help="Show version", action="store_true")
    return parser.parse_args()


def print_version():
    """Log version information."""
    log.info(
        "Python interpreter version: %d.%d.%d",
        sys.version_info.major,
        sys.version_info.minor,
        sys.version_info.micro,
    )
    log.info(
        "insights-content-template-renderer version: %s",
        pkg_resources.get_distribution("insights-content-template-renderer").version
    )


def command_line():
    """Command line handler for this insights_content_template_renderer."""
    args = parse_args()

    CustomLogger.logging_config = args.config["logging"]
    if args.version:
        logging.basicConfig(format="%(message)s", level=logging.INFO)
        print_version()
        sys.exit(0)
    else:
        WebServer(app, {"bind": args.config["host"] + ":" + str(args.config["port"])}).run()


class CustomLogger(glogging.Logger):
    """Custom logger for Gunicorn log messages."""

    logging_config = None

    def setup(self, cfg):
        """Configure Gunicorn application logging configuration."""
        print(self.logging_config)
        print(self.logging_config)

        logging.config.dictConfig(self.logging_config)


class WebServer(base.BaseApplication):
    """Gunicorn WSGI Web Server."""

    def init(self, parser, opts, args):
        pass

    def __init__(self, webapp, options):
        """Initialize server object."""
        self.options = options or {}
        self.application = webapp
        super().__init__()

    def load(self):
        """Return WSGI application."""
        return self.application

    def load_config(self):
        """Load configuration into Gunicorn."""
        self.cfg.set('logger_class', CustomLogger)
        self.cfg.set('worker_class', 'uvicorn.workers.UvicornWorker')
        self.cfg.set('pythonpath', 'insights_content_template_renderer')
        if 'bind' in self.options:
            self.cfg.set('bind', self.options["bind"])


if __name__ == "__main__":
    filepath = Path(__file__).parents[0].with_name("config.json")
    with open(filepath, encoding='UTF-8') as f:
        CustomLogger.logging_config = json.load(f)["logging"]
    WebServer(app, {}).run()
