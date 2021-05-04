import unittest
import socutils
import pymongo
import json
import requests_mock
from socutils.exceptions import *

test_host = '127.0.0.1'
test_port = 5000
test_url = 'http://{0}:{1}'.format(test_host, test_port)


class LogTestCase(unittest.TestCase):
    pass


class EventsAPITestCase(unittest.TestCase):
    """ Тестирование EventsAPIClient с Requests моками. """

    def setUp(self):
        # надо очищать базу
        #mongo_client.other.test.delete_many({})
        self.ec = socutils.EventsAPIClient(
            test_host, test_port, organization='other', device='test')

    @requests_mock.Mocker()
    def test_send_single_event(self, m):
        m.post(test_url + '/event/other', text=json.dumps([{'result': 'success'}]))
        event = {
            'name': 'Petrovich',
            'desc': 'Petrovich did something bad',
            'pc': 'Petrovich-PC'
        }
        self.ec.send_event(event)

    @unittest.skip
    @requests_mock.Mocker()
    def test_send_events_batch(self):
        events_batch = [
            {
                'name': 'Petrovich',
                'desc': 'Petrovich did something bad',
                'pc': 'Petrovich-PC'
            },
            {
                'name': 'Ivanich',
                'desc': 'Ivanich is pwned',
                'pc': 'Ivanich-PC'
            }
        ]
        self.ec.send_event(events_batch)

    @unittest.skip
    @requests_mock.Mocker()
    def test_general_send_single(self):
        event = {
            'name': 'Petrovich',
            'desc': 'Petrovich did something bad',
            'pc': 'Petrovich-PC'
        }
        self.ec.send(event)

    @unittest.skip
    @requests_mock.Mocker()
    def test_general_send_batch(self):
        events_batch = [
            {
                'name': 'Petrovich',
                'desc': 'Petrovich did something bad',
                'pc': 'Petrovich-PC'
            },
            {
                'name': 'Ivanich',
                'desc': 'Ivanich is pwned',
                'pc': 'Ivanich-PC'
            }
        ]
        self.ec.send(events_batch)

    @requests_mock.Mocker()
    def test_identical_events(self, m):
        m.post(test_url + '/event/other', [json.dumps([{'result': 'success'}]),
                                           json.dumps([{'result': 'error'}])])
        event = {
            'name': 'Petrovich',
            'desc': 'Petrovich did something bad',
            'pc': 'Petrovich-PC'
        }
        self.ec.send_event(event)
        self.ec.send_event(event)

    @requests_mock.Mocker()
    def test_status_up(self, m):
        m.get(test_url + '/status', text='Up', status_code=200)
        self.assertTrue(self.ec.status)

    @requests_mock.Mocker()
    def test_status_down(self, m):
        m.get(test_url + '/status', text='', status_code=404)
        self.assertFalse(self.ec.status)


if __name__ == '__main__':
    unittest.main()
