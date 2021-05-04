import json
import logging
import time
from typing import Dict

from socutils.exceptions import KafkaSettingsError, KafkaProducerError

logger = logging.getLogger(__name__)


class Message:
    def __init__(self):
        self.value = None
        self.topic = None
        self.partition = None
        self.offset = None
        self.key = None


class Consumer:
    consumer_settings = {}
    running = False

    def __init__(self,
                 servers,
                 group_id,
                 topics,
                 auth_params,
                 enable_auto_commit=False,
                 auto_offset_reset='earliest',
                 more_settings: dict = None
                 ):

        if len(servers) == 0:
            raise KafkaSettingsError('Empty servers')
        if not group_id:
            raise KafkaSettingsError('GroupId must be not empty')
        if not isinstance(topics, list):
            raise KafkaSettingsError('Topics must be a list')
        if len(topics) == 0:
            raise KafkaSettingsError('Empty topics')

        self.servers = servers
        self.topics = topics
        self.group_id = group_id
        self.enable_auto_commit = enable_auto_commit
        self.auto_offset_reset = auto_offset_reset
        self.consumer = None
        self.auth_params = auth_params

        self.__edit_settings()
        self.consumer_settings = {
            "api.version.request": True,
            "enable.auto.commit": self.enable_auto_commit,
            "group.id": self.group_id,
            "bootstrap.servers": self.servers,
            "default.topic.config": {"auto.offset.reset": self.auto_offset_reset}
        }
        self.consumer_settings.update(self.auth_params)
        if more_settings:
            self.consumer_settings.update(more_settings)

    def __edit_settings(self):
        if self.auth_params:
            old_settings = self.auth_params.copy()
            self.auth_params = {}
            self.auth_params = {'security.protocol': 'ssl',
                                'ssl.key.location': old_settings['ssl_keyfile'],
                                'ssl.certificate.location': old_settings['ssl_certfile'],
                                'ssl.ca.location': old_settings['ssl_cafile']}

        if isinstance(self.servers, list):
            old_servers = list(self.servers)
            self.servers = ','.join(old_servers)

    def create_consumer(self):
        from confluent_kafka import Consumer as ConfluentConsumer
        self.consumer = ConfluentConsumer(self.consumer_settings)
        self.consumer.subscribe(topics=self.topics)
        return self.consumer

    def read_topic(self):
        self.running = True
        while self.running:
            message = self.consumer.poll()
            msg = message.value().decode()
            if msg == 'Broker: No more messages':
                time.sleep(1)
                continue
            try:
                json.loads(msg)
            except json.decoder.JSONDecodeError:
                continue
            application_message = Message()
            application_message.value = json.loads(msg)
            application_message.topic = message.topic()
            application_message.partition = message.partition()
            application_message.offset = message.offset()
            application_message.key = message.key()

            yield application_message

    def __del__(self):
        self.consumer.close()


class Producer:

    def __init__(self, servers, auth_params, json_encoder_cls=None, more_settings: Dict = None):
        if len(servers) == 0:
            raise KafkaSettingsError('Empty servers')
        self.servers = servers
        self.producer = None
        self.auth_params = auth_params
        self.json_encoder_cls = json_encoder_cls
        self.__edit_settings()
        self.producer_settings = {
            "api.version.request": True,
            "bootstrap.servers": self.servers
        }
        self.producer_settings.update(self.auth_params)
        if more_settings:
            self.producer_settings.update(more_settings)

    def __edit_settings(self):
        if self.auth_params:
            old_settings = self.auth_params.copy()
            self.auth_params = {}
            self.auth_params = {'security.protocol': 'ssl',
                                'ssl.key.location': old_settings['ssl_keyfile'],
                                'ssl.certificate.location': old_settings['ssl_certfile'],
                                'ssl.ca.location': old_settings['ssl_cafile']}
        if isinstance(self.servers, list):
            old_servers = list(self.servers)
            self.servers = ','.join(old_servers)

    def create_producer(self):
        from confluent_kafka import Producer as ConfluentProducer

        self.producer = ConfluentProducer(self.producer_settings)
        return self.producer

    def send_json(self, topic, json_data):
        """?????"""
        if not isinstance(json_data, dict):
            raise KafkaProducerError('json_data must be a dict')
        self.producer.poll(0)
        self.producer.produce(topic, self.serialize_message(json_data))
        self.flush()

    def send(self, **kwargs):
        if not isinstance(kwargs.get('json_data'), dict):
            raise KafkaProducerError('json_data must be a dict')
        self.producer.poll(0)
        self.producer.produce(topic=kwargs.get('topic'),
                              key=kwargs.get('key'),
                              value=self.serialize_message(kwargs.get('json_data')))
        self.flush()

    def flush(self):
        """block until all async messages are sent"""
        self.producer.flush()

    @staticmethod
    def on_send_success(record_metadata):
        """if success"""
        return True

    @staticmethod
    def on_send_error(excp):
        """on error"""
        # TODO make raise
        return False

    def send_json_callback(self, topic, json_data):
        """produce asynchronously with callbacks"""

        def delivery_report(err, msg):
            """ Called once for each message produced to indicate delivery result.
                Triggered by poll() or flush(). """
            if err is not None:
                raise KafkaProducerError('Message delivery failed: {}'.format(err))

        if not isinstance(json_data, dict):
            raise KafkaProducerError('json_data must be a dict')

        self.producer.poll(0)
        self.producer.produce(topic, self.serialize_message(json_data), callback=delivery_report)

    def serialize_message(self, message):
        return json.dumps(message, cls=self.json_encoder_cls).encode()


if __name__ == '__main__':
    pass
