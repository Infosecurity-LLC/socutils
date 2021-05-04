"""
    Коннектор для Messila API
"""
import logging
import requests
from urllib3.exceptions import InsecureRequestWarning
import urllib3
import json
from datetime import datetime
import decimal
from bson.objectid import ObjectId
from socutils.exceptions import MessilaApiExceptions

urllib3.disable_warnings(InsecureRequestWarning)

logger = logging.getLogger('socutils.connectors.MessilaApiClient')


class MessilaApiClient:
    def __init__(self, setting):
        self.__api = setting
        self.__s = requests.Session()

    @staticmethod
    def _cast(data_dict):
        """ приведение типов"""
        for k, v in data_dict.items():
            if isinstance(v, datetime):
                data_dict[k] = data_dict[k].isoformat()
            if isinstance(v, decimal.Decimal):
                data_dict[k] = int(data_dict[k])
            if isinstance(v, ObjectId):
                data_dict[k] = str(data_dict[k])
            try:
                data_dict[k] = int(data_dict[k])
            except (ValueError, TypeError):
                pass

        return data_dict

    def status(self):
        """
         Статус api
        :return:
        """
        return requests.get(url='{}/status'.format(self.__api['host']), verify=self.__api.get('verify'))

    def send_alert(self, alert_row, api_method, organization, segment="default", payload=None):
        """
         Отправить событие в api
        :param alert_row:   Что отправляем
        :param api_method   Куда отправляем
        :param segment:     Сегмент
        :param payload: любые полезные данные, которые должны быть доавлены в отправляемый словарь
        :param organization: Организация, под которой будет регистрироваться событие.
        :return:
        """
        try:
            usr, pwd = self.__api[organization]['login'], self.__api[organization]['password']
        except KeyError as err:
            raise MessilaApiExceptions(
                'Settings error, current organization {}, does not have params in setting. Error: {}'.format(
                    organization, err))

        def merge_two_dicts(x, y):
            """ Объединение словарей, после 3.5 можно делать {**x, **y}, но мы старпёры, сидим на 3.4"""
            z = x.copy()
            z.update(y)
            return z

        if not isinstance(alert_row, dict):
            logger.error('Incorrect data format from kafka. It is not Dict! [{}]'.format(alert_row))
            return False

        if isinstance(payload, dict):
            alert_row = merge_two_dicts(alert_row, payload)

        alert_row.update(segment=segment)
        alert_data = self._cast(alert_row)
        try:
            res = self.__s.post(url='{}{}'.format(self.__api['host'], api_method),
                                headers={'Content-type': 'application/json', 'Accept': 'application/json'},
                                auth=(usr, pwd),
                                verify=self.__api.get('verify'),
                                data=json.dumps(alert_row))
        except Exception as err:
            logger.error(err)
            return False
        if res.status_code != 200:
            _content = 'Error'
            try:
                _content = json.loads(res.content.decode('utf-8')).get('detail')
            except ValueError:
                logging.error('Api receive error')
            logger.error('Messila bot rejected new alert: {} - [status_code:{} - {}]'.format(
                alert_data,
                res.status_code,
                _content
            ))
            return False
        logger.debug('Messila bot accepted new alert. {} '.format(alert_data))
        return True
