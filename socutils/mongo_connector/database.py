from .client import Client


class Database(object):
    __instance = None

    def __init__(self, client: Client, label: str = None):
        """
        Database object helps creating instance of mongo connector

        :param client: mongo_client.Client instance that used for getting config options
        :param label: Label of the database connected to
        """
        if client is None:
            raise ValueError('Client instance should be provided to database')
        self._client = client

        if label is None:
            label = client.default_db_label
        self._label = label

    @classmethod
    def create(cls, label: str, host: str, port: int, *args, **kwargs):
        """
        Creates mongo_client.Database instance from specified params

        :param label: Label of the database connected to
        :param host: MongoDB host, that'll be used for database connector creating
        :param port: MongoDB port, that'll be used for database connector creating
        :param args: additional parameters for mongo_client.Client instance creation
        :param kwargs: additional parameters for mongo_client.Client instance creation
        :return: Database instance
        """
        return cls(Client(host=host, port=port, *args, **kwargs), label)

    @property
    def label(self) -> str:
        """
        Label of the database connected to

        :return: Database label
        """
        return self._label

    @label.setter
    def label(self, label: str):
        """
        Setter for mongo_client.Database.label

        :param label: New database label
        """
        self.__instance = None
        self._label = label

    @property
    def client(self) -> Client:
        """
        mongo_client.Client instance that used for getting config options

        :return: mongo_client.Client instance
        """
        return self._client

    @client.setter
    def client(self, client: Client):
        """
        Setter for mongo_client.Database.client

        :param client: new mongo_client.Database.client
        """
        self.__instance = None
        self._client = client

    def set_new_client(self, host: str, port: int, *args, **kwargs):
        """
        Creates new client from specified params and set it to mongo_client.Database.client

        :param host: MongoDB host, that'll be used for database connector creating
        :param port: MongoDB port, that'll be used for database connector creating
        :param args: additional parameters for mongo_client.Client instance creation
        :param kwargs: additional parameters for mongo_client.Client instance creation
        """
        self.__instance = None
        self._client = Client(host=host, port=port, *args, **kwargs)

    def get_instance(self, label: str = None, *args, **kwargs):
        """
        Getting pymongo.MongoClient instance with provided connection parameters

        :param label: Label of the database connected to, default value is self.label

        :return: pymongo.MongoClient instance
        """
        from pymongo import MongoClient

        if label is None:
            label = self.label
            if label is None:
                raise ValueError('Database label should be provided')
            if self.__instance is None:
                self.__instance = MongoClient(self.client.mongo_uri)[label]
            instance = self.__instance
        else:
            instance = MongoClient(self.client.mongo_uri, *args, **kwargs)[label]
        return instance
