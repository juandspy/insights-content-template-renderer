"""
Custom logger using Loguru.
Source: https://gist.github.com/Riki-1mg/ca3cf9cebdc0da29ed55234b56da3a00
"""

import logging
import sys
import json
from pathlib import Path
from loguru import logger


class InterceptHandler(logging.Handler):
    """
    Custom logging handler.
    """

    loglevel_mapping = {
        50: "CRITICAL",
        40: "ERROR",
        30: "WARNING",
        20: "INFO",
        10: "DEBUG",
        0: "NOTSET",
    }

    def emit(self, record):
        """
        Emits the formatted message to the logging output.

        :param record: record to be logged
        :return: None
        """
        try:
            level = logger.level(record.levelname).name
        except AttributeError:
            level = self.loglevel_mapping[record.levelno]

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        log = logger.bind(request_id="app")
        log.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class Logger:
    """
    Class providing methods for building a logger with custom configuration.
    """

    @classmethod
    def make_logger(cls, config_path: Path):
        """
        Parses configuration and creates a logger.

        :param config_path: path to JSON configuration of the logger
        :return: the created logger
        """
        config = cls.load_logging_config(config_path)
        logging_config = config.get("logger")
        custom_logger = cls.customize_logging(logging_config)

        return custom_logger

    @classmethod
    def customize_logging(cls, logging_config: dict):
        """
        Creates the logger based on given parameters.

        :param logging_config: dictionary with logging configuration
        :param retention: log retention
        :return: configured logger
        """
        log_path = None
        if (
            logging_config.get("path") is not None
            and logging_config.get("filename") is not None
        ):
            log_path = Path(logging_config.get("path")) / logging_config.get("filename")

        logger.remove()
        logger.add(
            sys.stdout,
            enqueue=True,
            backtrace=True,
            level=logging_config.get("level").upper(),
            format=logging_config.get("format"),
        )
        if log_path is not None:
            logger.add(
                str(log_path),
                rotation=logging_config.get("rotation"),
                retention=logging_config.get("retention"),
                enqueue=True,
                backtrace=True,
                level=logging_config.get("level").upper(),
                format=logging_config.get("format"),
            )
        logging.basicConfig(handlers=[InterceptHandler()], level=0)
        logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
        for _log in ["uvicorn", "uvicorn.error", "fastapi"]:
            _logger = logging.getLogger(_log)
            _logger.handlers = [InterceptHandler()]

        return logger.bind(request_id=None, method=None)

    @classmethod
    def load_logging_config(cls, config_path):
        """
        Loads logger configuration from the file path.

        :param config_path: path of the configuration file
        :return: dictionary with logger parameters
        """
        config = None
        with open(config_path, encoding="UTF-8") as config_file:
            config = json.load(config_file)
        return config


filepath = Path(__file__).parents[0].with_name("logging_config.json")
app_log = Logger.make_logger(filepath)
