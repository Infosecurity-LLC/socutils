""" TODO rewrite as Singleton ?"""
import logging
import zmq
import time
from socutils.exceptions import MQReceiveError, EventRegistrationError

logger = logging.getLogger(__name__)


class RequestClient:
    def __init__(self):
        self._port = None
        self._host = None
        self._zmq_socket = None

    def connect(self, host, port):
        self._host = host
        self._port = port
        if not isinstance(self._host, str):
            raise TypeError('Server ip is required, check setting')
        if not isinstance(self._port, int):
            raise TypeError('Server port is required check setting')
        context = zmq.Context()
        self._zmq_socket = context.socket(zmq.REQ)
        self._zmq_socket.setsockopt(zmq.LINGER, 0)
        # Maximum time before a recv operation returns with EAGAIN
        self._zmq_socket.setsockopt(zmq.RCVTIMEO, 10 * 1000)
        # self._zmq_socket.setsockopt(zmq.SNDTIMEO, 0)
        self._zmq_socket.connect("tcp://%s:%s" % (self._host, self._port))

    def send_json(self, data):
        if not isinstance(data, dict):
            raise TypeError('Data is not dictionary')
        try:
            self._zmq_socket.send_json(data)
            ret = self._zmq_socket.recv_json()
            return ret
        except AttributeError as err:
            raise IOError("Socket is down. Reason {}".format(err))
        except (zmq.error.Again, zmq.error.ZMQError) as err:
            raise MQReceiveError("Remote server not available: {}".format(err))

    # TODO Make async version
    def send_event(self, data, sleep_time=240, interval=5):
        time.sleep(interval)
        logger.debug('Event send to bot: {}'.format(data))
        try:
            answer = self.send_json(data)
        except (IOError, TypeError) as err:
            logger.critical(err)
            return
        except MQReceiveError as err:
            logger.critical('Critical error. {}'.format(err))
            raise EventRegistrationError(data)
        if answer.get('status') == 'pass':
            logger.info('Event success registration. Event: {}'.format(data))
        elif answer.get('status') == 'reject':
            logger.warning('{0} rejected, sleep {1} seconds'.format(
                data, sleep_time))
            time.sleep(sleep_time)
            self.send_event(data, sleep_time)
        else:
            raise EventRegistrationError(data)

    @staticmethod
    def connection_test(host, port):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.setsockopt(zmq.LINGER, 0)
        socket.connect("tcp://%s:%s" % (host, port))
        # Отправить тестовое сообщение. Ресивер должен принимать такие.
        socket.send_json({"msg": "test"})
        # Создаем пулер, чтобы посчитать таймаут:
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)
        if poller.poll(5 * 1000):  # 5s в милисекундах
            socket.recv_json()
        else:
            logger.critical('REMOTE server {}: {} is down'.format(host, port))
            raise IOError("Timeout processing auth request")
        socket.close()
        context.term()


if __name__ == '__main__':
    pass
