import socket
from contextlib import contextmanager
import logging
import json

logger = logging.getLogger("socutils.connectors.NXLogSender")


class NXLogSender:
    def __init__(self, host, port):
        self.__setting = (host, port)
        self.sock = None

    # по класике:
    def connect(self):
        try:
            self.sock = socket.create_connection(self.__setting)
        except ConnectionRefusedError:
            logger.error('Нет доступа до принимающего сервера')
        except Exception as err:
            logger.error(err)

    def send_event(self, message: dict):
        try:
            jmessage = json.dumps(message)
            logger.debug("Sending message to NXLog {}".format(jmessage))
            self.sock.send("{}\n".format(str(jmessage)).encode("utf-8"))

        except BrokenPipeError:
            logger.error('Сессия к NXLog оборвалась. Событие не было отправлено {}'.format(message))
            return False
        except AttributeError:
            logger.error('Событие не было отправлено {}'.format(message))
            return False
        except Exception as err:
            logger.error(err)
            return False
        return True

    def close(self):
        try:
            self.sock.close()
        except AttributeError:
            logger.error('Нельзя закрыть несуществующую сессию')
        except Exception as err:
            logger.error(err)

    # //по класике

    # модерн:
    @contextmanager
    def tcp_connection_to(self, *args, **kwargs):
        s = socket.create_connection(*args, **kwargs)
        yield s
        s.close()

    def send_list(self, message_list: list):
        with self.tcp_connection_to(self.__setting) as conn:
            for message in message_list:
                jmessage = json.dumps(message)
                logger.debug("Sending message to NXLog {}".format(jmessage))
                try:
                    conn.send("{}\n".format(str(jmessage)).encode('utf-8'))
                except BrokenPipeError:
                    logger.error('Сессия к NXLog оборвалась. Событие не было отправлено {}'.format(message))

    def send(self, message: dict):
        with self.tcp_connection_to(self.__setting) as conn:
            try:
                jmessage = json.dumps(message)
                logger.debug("Sending message to NXLog {}".format(jmessage))
                conn.send("{}\n".format(str(jmessage)).encode('utf-8'))
            except BrokenPipeError:
                logger.error('Сессия к NXLog оборвалась. Событие не было отправлено {}'.format(message))
    # //модерн

#
# if __name__ == '__main__':
#     nxlog = NXLogSender("localhost", "9090")
#     messages = [dict(mes='test'), dict(mes='test2')]
#
#     nxlog.connect()
#     for message in messages:
#         nxlog.send_event(message)
#     nxlog.close()

# or

# nxlog.send_list(messages)
