import unittest
from socutils import EventsAPIClient
from socutils.exceptions import ServiceIDMissedError, QueueIDMissedError


class EventsAPIClientTestCase(unittest.TestCase):
    """ Тестирование методов EventsAPICLient. """

    def test_queue_arg_missed(self):
        with self.assertRaises(QueueIDMissedError):
            EventsAPIClient(
                '127.0.0.1',
                api_port=5000,
                organization='other',
                service=3,
                device='test',
                ssl=False)

    def test_service_arg_missed(self):
        with self.assertRaises(ServiceIDMissedError):
            EventsAPIClient(
                '127.0.0.1',
                api_port=5000,
                organization='other',
                queue=28,
                device='test',
                ssl=False)

    def test_prepare_event(self):
        ec = EventsAPIClient(
            '127.0.0.1',
            api_port=5000,
            organization='other',
            queue=28,
            service=3,
            device='test',
            ssl=False)
        test_event = {
            'name': 'Ivan Petrovich',
            'pc': 'El-Petro-PC'
        }
        result_event = test_event.copy()
        result_event.update({
            '_service': 3,
            '_queue': 28,
            '_organization': 'other',
            'device': 'test'
        })
        ec.prepare_event(test_event)
        self.assertEqual(result_event, test_event)


if __name__ == '__main__':
    unittest.main()
