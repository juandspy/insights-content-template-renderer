"""Sentry SDK configuration and utility functions."""

import logging
import os

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


def get_event_level():
    """Get level of events to monitor (errors only, or error and warnings)."""
    if os.environ.get("SENTRY_CATCH_WARNINGS", False):
        return logging.WARNING
    return logging.ERROR


def init_sentry(
        dsn=os.environ.get("SENTRY_DSN", None),
        transport=None,
        environment=os.environ.get("SENTRY_ENVIRONMENT", None)):
    """Configure and initialize sentry SDK for this project."""
    if dsn:
        logging.getLogger(__name__).info("Initializing sentry")
        sentry_logging = LoggingIntegration(level=logging.INFO, event_level=get_event_level())

        sentry_sdk.init(
            dsn=dsn,
            ca_certs="/etc/pki/tls/certs/ca-bundle.crt",
            integrations=[sentry_logging],
            max_breadcrumbs=15,
            transport=transport,
            environment=environment,
        )
