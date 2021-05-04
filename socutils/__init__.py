import uuid
import logging
import os
import inspect
import yaml
import ssl

from . import mail
from . import exceptions
from . import reports
from . import log

from .events_api import EventsAPIClient, EventsBatch
from .messila_api import MessilaApiClient
from .nxlog_sender import NXLogSender
# from . import connectors

logger = logging.getLogger('socutils')


def get_event_id(service_id='0000'):
    """ Возврат id для отправки на бота/API.
        Сервис должен иметь свой service_id в setting.
    """
    event_id = "{0}-{1}".format(uuid.uuid4(), service_id)
    logger.debug('event id: {}'.format(event_id))
    return event_id


def get_settings(settings_file='data/setting.yaml'):
    """
        Получение конфигурации из yaml файла.
    """
    settings_path = os.path.join(os.getcwd(), settings_file)
    if not os.path.exists(settings_path):
        logger.error(f'Error getting setting. Check your settings file in {settings_path}')
        raise exceptions.SettingsFileNotExistError(f"File {settings_path} doesn't exist")
    with open(settings_path, encoding='utf-8') as f:
        setting = yaml.load(f.read(), Loader=yaml.FullLoader)
    logger.debug('settings loaded: {}'.format(setting))
    return setting


def get_cassandra_ssl_opts(ssl_cert=None):
    if ssl_cert:
        ssl_opts = {
            'ca_certs': ssl_cert,
            'ssl_version': ssl.PROTOCOL_TLSv1,
            'cert_reqs': ssl.CERT_REQUIRED}
    else:
        ssl_opts = None
    logger.debug('ssl options: {}'.format(ssl_opts))
    return ssl_opts


def get_parent_settings(settings_file='data/setting.yaml'):
    """
        Получение конфигурации из yaml файла вне зависимости от
        текущей рабочей директории.
    """
    if settings_file.startswith('/') and os.path.exists(settings_file):
        settings_path = settings_file
    else:
        stack = inspect.stack()
        if len(stack) == 1:
            raise exceptions.InvalidCallStackError()
        script_filename = stack[1][1]
        script_path = os.path.abspath(os.path.dirname(script_filename))
        settings_path = os.path.join(script_path, settings_file)
    if not os.path.exists(settings_path):
        logger.error(f'Error getting setting. Check your settings file in {settings_path}')
        raise exceptions.SettingsFileNotExistError(f"File {settings_path} doesn't exist")
    with open(settings_path, 'r') as f:
        setting = yaml.load(f.read(), Loader=yaml.FullLoader)
    return setting


def setup_logging(logger, logging_settings, log_path=None):
    pass
