from urllib.parse import quote_plus


class Client(object):
    __uri = None

    def __init__(self, app=None, host: str = None, port: int = None, user: str = None, password: str = None,
                 default_db: str = None):
        """
        Object that stores configuration options for mongo_connector package

        Usually shares config options for connect between threads or requests

        :param app: Flask app with config
        :param host: MongoDB host, that'll be used for database connector creating
        :param port: MongoDB port, that'll be used for database connector creating
        :param user: MongoDB user, that'll be used for database connector creating
        :param password: MongoDB password, that'll be used for database connector
        :param default_db: Label of database, that'll be used if you don't provide any other db label in
        mongo_client.Database initialization
        """
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._default_db = default_db

        if app is not None:
            self.init_app(app)

    def init_app(self, app, host: str = None, port: int = None, user: str = None, password: str = None,
                 default_db: str = None):
        """
        Initialize Client with Flask.app.config

        :param app: Flask app with config
        :param host: MongoDB host, that'll be used for database connector creating
        :param port: MongoDB port, that'll be used for database connector creating
        :param user: MongoDB user, that'll be used for database connector creating
        :param password: MongoDB password, that'll be used for database connector
        :param default_db: Label of database, that'll be used if you don't provide any other db label in
        mongo_client.Database initialization
        """
        if host is None:
            host = app.config.get('MONGODB_HOST')
        if host is None:
            raise ValueError('host is not provided for mongo_client instance')
        self._host = host

        if port is None:
            port = app.config.get('MONGODB_PORT')
        if port is None:
            raise ValueError('port is not provided for mongo_client instance')
        self._port = port

        if user is None:
            user = app.config.get('MONGODB_USER')
        self._user = user

        if password is None:
            password = app.config.get('MONGODB_PASSWORD')
        self._password = password

        if default_db is None:
            default_db = app.config.get('DEFAULT_DB_LABEL')
        self._default_db = default_db

    @property
    def host(self) -> str:
        """
        MongoDB host, that'll be used for database connector creating

        :return: string with host
        """
        return self._host

    @host.setter
    def host(self, host: str):
        """
        Sets new host to attribute of Client

        :param host: new host string
        """
        self._host = host

    @property
    def port(self) -> int:
        """
        MongoDB port, that'll be used for database connector creating

        :return: int with port
        """
        return self._port

    @port.setter
    def port(self, port: int):
        """
        Sets new port to attribute of Client

        :param port: new port
        """
        self._port = port

    @property
    def default_db_label(self) -> str:
        """
        Label of database, that'll be used if you don't provide any other db label in
        mongo_client.Database initialization

        :return: Default database label
        """
        return self._default_db

    @default_db_label.setter
    def default_db_label(self, db_label: str):
        """
        Setter for mongo_client.default_db_label

        :param db_label: New database label
        """
        self._default_db = db_label

    @property
    def mongo_uri(self):
        """
        Getting url for connection to mongodb by properly formatted string

        :return: str with mongodb URI
        """
        if not self.__uri:
            if self._user and self._password:
                user = quote_plus(self._user)
                password = quote_plus(self._password)
                self.__uri = f"mongodb://{user}:{password}@{self.host}:{self.port}"
            else:
                self.__uri = f"mongodb://{self.host}:{self.port}"
        return self.__uri
