import logging
from raven.handlers.logging import SentryHandler
from raven.conf import setup_logging

socutils_logger = logging.getLogger('socutils.log')


def add_file_handler(logger, log_path, log_level='INFO',
                     log_format='%(asctime)s - %(message)s',
                     datefmt='%d-%m-%Y %H:%M:%S'):
    if not log_path:
        socutils_logger.warning("log_path isn't set, skipping.")
        return
    fh = logging.FileHandler(log_path)
    fh.setLevel(log_level)
    formatter = logging.Formatter(log_format, datefmt=datefmt)
    fh.setFormatter(formatter)
    logger.addHandler(fh)


def add_sentry_handler(sentry_url, log_level='INFO'):
    if not sentry_url:
        socutils_logger.warning("sentry_url isn't set, skipping.")
        return
    handler = SentryHandler(sentry_url)
    handler.setLevel(log_level)
    setup_logging(handler)
