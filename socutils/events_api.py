"""
    Коннектор для OTRS REST API
"""
import logging
import json
import requests

from socutils.exceptions import EmptyDeviceError, EventSendError
from socutils.exceptions import BatchOrganizationError, EventSearchError, EmptyOrganizationError
from socutils.exceptions import ServiceIDMissedError, QueueIDMissedError


logger = logging.getLogger('socutils.connectors.eventsapi')
headers = {'Content-Type': 'application/json'}


class EventsBatch:
    """ Отправка нескольких событий на Events REST API сервис. """

    def __init__(self):
        self._batch = []

    def add_events_list(self, events_list):
        if not isinstance(events_list, list):
            raise TypeError('events_list should be a list')
        self._batch.append(events_list)

    def add_event(self, event):
        if not isinstance(event, dict):
            raise TypeError('event should be a dict')
        self._batch.append(event)

    def get_events(self):
        return self._batch


class EventsAPIClient:
    """ Клиент для взаимодействия с Events REST API сервисом. """

    def __init__(self, api_host, api_port=8080, device=None,
                 organization=None, service=None, queue=None, ssl=False):
        """ :param api_host: хост Events REST API, без указания протокола и
            порта.
            :type api_host: string
            :param api_port: порт Events REST API.
            :type api_port: integer
            :param device: девайс, породивший событие.
            :type device: string
            :param organization: организация, к которой относится событие.
            :type organization: string
            :param service: сервис OTRS, к которому относится событие.
            :type service: integer
            :param queue: очередь OTRS, к которой относится событие.
            :type queue: integer
            :param ssl: использовать ли https соединение.
            :type ssl: boolean
        """
        proto = "https" if ssl else "http"
        if not isinstance(api_port, int):
            raise TypeError("api_port has invalid value type (should be int)")
        if api_host.startswith('https://'):
            api_host = api_host[8:]
        elif api_host.startswith('http://'):
            api_host = api_host[7:]
        self.status_url = "{0}://{1}:{2}/status".format(
            proto, api_host.strip('/'), api_port)
        self.event_url = "{0}://{1}:{2}/event/".format(
            proto, api_host.strip('/'), api_port)
        self.event_search = "{0}://{1}:{2}/search/".format(
            proto, api_host.strip('/'), api_port)
        self.device = device
        self.organization = organization
        self.service = service
        self.queue = queue
        if self.service is None:
            raise ServiceIDMissedError()
        if self.queue is None:
            raise QueueIDMissedError()
        if not self.device:
            logger.warning('device field is not set. Remember to set it in '
                           'events manually')
        if not self.organization:
            logger.warning('organization field is not set. Remember to set it '
                           'in events manually')

    def prepare_event(self, event):
        """ Подготовка события к отправке.

            WARN: Модифицирует оригинальное событие!
        """
        event['device'] = event.get('device', self.device)
        if not event['device']:
            raise EmptyDeviceError()
        event['_organization'] = event.get('_organization', self.organization)
        if not event['_organization']:
            logger.warning("'_organization' field is not set. Entry will be"
                           " added to 'other' table")
            event['_organization'] = 'other'
        event['_service'] = self.service
        event['_queue'] = self.queue
        return event

    def send_event(self, event):
        """ Отсылка уведомления о новом событии на OTRS REST API.

            :param event: событие для отправки.
            :type event: dictionary
        """

        event = self.prepare_event(event)
        url = self.event_url + event['_organization']
        try:
            resp = requests.post(url, data=json.dumps(event), headers=headers)
        except requests.exceptions.ConnectionError:
            raise EventSendError("connection error")
        logger.debug('events api response <{0}>: {1}'.format(
            resp.status_code, resp.text))
        if resp.status_code != 200:
            logger.error('bad status code {}'.format(resp.status_code))
            raise EventSendError('bad status code {}'.format(resp.status_code))
        result_data = resp.json()
        if not result_data or not isinstance(result_data, list):
            raise EventSendError()
        result = result_data[0].get('result')
        if result == 'success':
            logger.debug("event {} is sent".format(event))
            return True
        elif result == 'reject':
            logger.debug("event {} is rejected".format(event))
            return False
        else:
            logger.warning("error occured while sending event {}".format(
                event))
            raise EventSendError()

    def search_event(self, query):
        """ Поиск события по произвольным полям.

            :param query: запрос на поиск события в виде словаря с
            искомыми полями.
            :type query: dictionary
        """
        if not query.get('device'):
            query.update({'device': self.device})
        if query.get('organization'):
            self.organization = query.get('organization')

        if not query.get('device'):
            raise EmptyDeviceError()
        if not self.organization:
            raise EmptyOrganizationError()
        url = self.event_search + self.organization
        try:
            resp = requests.post(url, data=json.dumps(query), headers=headers)
        except requests.exceptions.ConnectionError:
            raise EventSendError("connection error")
        if resp.status_code == 200:
            result_data = resp.json()
            logger.debug("event success found: {}".format(query))
            return result_data
        elif resp.status_code == 404:
            logging.debug("event not found: {}".format(query))
            return False
        else:
            raise EventSearchError()

    def send_batch(self, events_batch):
        """ Отправка набора событий на OTRS REST API. """

        if not isinstance(events_batch, EventsBatch):
            raise TypeError()
        events, orgs = [], set()
        for event in events_batch.get_events():
            events.append(self.prepare_event(event))
            orgs.add(events['_organization'])
        if len(orgs) != 1:
            raise BatchOrganizationError()
        url = self.event_url + orgs.pop()
        try:
            resp = requests.post(url, data=json.dumps(events), headers=headers)
        except requests.exceptions.ConnectionError:
            raise EventSendError("connection error")
        if resp.status_code == 200:
            logger.debug("events batch {} is sent".format(events))
        else:
            raise EventSendError()

    def send(self, data):
        """ Отправка события или набора событий на OTRS REST API. """
        if isinstance(data, EventsBatch):
            self.send_batch(data)
        elif isinstance(data, dict):
            self.send_event(data)

    @property
    def status(self):
        """ Проверка доступности OTRS REST API. """
        resp = requests.get(self.status_url, headers=headers)
        if resp.status_code != 200 or resp.text != 'Up':
            return False
        return True
