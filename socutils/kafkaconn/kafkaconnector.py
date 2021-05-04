import json
import logging
from socutils.exceptions import KafkaSettingsError, KafkaProducerError, AuthError, AuthSettingError

logger = logging.getLogger(__name__)


class Consumer:
    def __init__(self, servers,
                 group_id,
                 topics,
                 auth_params,
                 enable_auto_commit=False,
                 auto_offset_reset='earliest'
                 ):
        if not isinstance(servers, list):
            raise KafkaSettingsError('Servers must be a list')
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

    def create_consumer(self):
        """ Пробуем поднять коннект с кафкой """
        from kafka import KafkaConsumer
        self.consumer = KafkaConsumer(
            bootstrap_servers=self.servers,
            api_version=(0, 10, 1),
            value_deserializer=JsonSerializer.deserialize,
            enable_auto_commit=self.enable_auto_commit,
            auto_offset_reset=self.auto_offset_reset,
            group_id=self.group_id,
            **self.auth_params
        )
        self.consumer.subscribe(topics=self.topics)
        return self.consumer

    def read_topic(self):
        for message in self.consumer:
            yield message

    def __del__(self):
        self.consumer.close()


class Producer:
    def __init__(self, servers, auth_params):
        if not isinstance(servers, list):
            raise KafkaSettingsError('Servers must be a list')
        if len(servers) == 0:
            raise KafkaSettingsError('Empty servers')
        self.servers = servers
        self.producer = None
        self.auth_params = auth_params

    def create_producer(self):
        from kafka import KafkaProducer
        self.producer = KafkaProducer(bootstrap_servers=self.servers,
                                      api_version=(0, 10, 1),
                                      key_serializer=JsonSerializer.serialize,
                                      value_serializer=JsonSerializer.serialize,
                                      **self.auth_params
                                      )
        return self.producer

    def send_json(self, topic, json_data):
        if not isinstance(json_data, dict):
            raise KafkaProducerError('json_data must be a dict')
        self.producer.send(topic, json_data)
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
        if not isinstance(json_data, dict):
            raise KafkaProducerError('json_data must be a dict')

        self.producer.send(topic, json_data).add_callback(self.on_send_success).add_errback(self.on_send_error)


class JsonSerializer(object):
    @staticmethod
    def serialize(value):
        return json.dumps(value).encode('utf-8')

    @staticmethod
    def deserialize(value):
        return json.loads(value.decode('utf-8'))
