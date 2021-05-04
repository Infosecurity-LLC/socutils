
class Connector:

    def __init__(self, app=None, host: str = None, port: int = None, username: str = None, database: str=None,
                 auth: str = None, configuration: dict = None, kerberos_service_name: str = None, password: str = None,
                 thrift_transport=None):
        """
        Connector object helps create an instance of the hive connector

        :param app: Flask app with config
        :param host: Hive host, that'll be used for Connector creating
        :param port: Hive port, that'll be used for Connector creating
        :param username: Hive username, that'll be used for Connector creating
        :param database: Hive database, that'll be used for Connector creating
        :param auth: Hive auth, that'll be used for Connector creating
        :param configuration: Hive configuration, that'll be used for Connector creating
        :param kerberos_service_name: Hive kerberos_service_name, that'll be used for Connector creating
        :param password: Hive password, that'll be used for Connector creating
        :param thrift_transport: Hive thrift_transport, that'll be used for Connector creating

        """
        self._host = host
        self._port = port
        self._username = username
        self._database = database
        self._auth = auth
        self._configuration = configuration
        self._kerberos_service_name = kerberos_service_name
        self._password = password
        self._thrift_transport = thrift_transport

        if app is not None:
            self.init_app(app)

    def init_app(self, app, host: str = None, port: int = None, username: str = None, database: str = None,
                 auth: str = None, configuration: str = None, kerberos_service_name: str = None, password: str = None,
                 thrift_transport: str = None):
        """
        Initialize Connector with Flask.app.config

        :param app: Flask app with config
        :param host: Hive host, that'll be used for Connector creating
        :param port: Hive port, that'll be used for Connector creating
        :param username: Hive username, that'll be used for Connector creating
        :param database: Hive database, that'll be used for Connector creating
        :param auth: Hive auth, that'll be used for Connector creating
        :param configuration: Hive configuration, that'll be used for Connector creating
        :param kerberos_service_name: Hive kerberos_service_name, that'll be used for Connector creating
        :param password: Hive password, that'll be used for Connector creating
        :param thrift_transport: Hive thrift_transport, that'll be used for Connector creating

        """
        if host is None:
            host = app.config.get('HIVE_HOST')
        if host is None:
            raise ValueError('host is not provided for database instance')
        self._host = host

        if port is None:
            port = app.config.get('HIVE_PORT')
        self._port = port

        if username is None:
            username = app.config.get('HIVE_USERNAME')
        self._username = username

        if database is None:
            database = app.config.get('HIVE_DATABASE')
        self._database = database

        if auth is None:
            auth = app.config.get('HIVE_AUTH')
        self._auth = auth

        if configuration is None:
            configuration = app.config.get('HIVE_CONFIGURATION')
        self._configuration = configuration

        if kerberos_service_name is None:
            kerberos_service_name = app.config.get('HIVE_KERBEROS_SERVICE_NAME')
        self._kerberos_service_name = kerberos_service_name

        if password is None:
            password = app.config.get('HIVE_PASSWORD')
        self._password = password

        if thrift_transport is None:
            thrift_transport = app.config.get('HIVE_THRIFT_TRANSPORT')
        self._thrift_transport = thrift_transport

    @property
    def host(self) -> str:
        """
        Hive host, that'll be used for Connector creating

        :return: string with host
        """
        return self._host

    @host.setter
    def host(self, host: str):
        """
        Sets new host to attribute of Connector

        :param host: new host string
        """
        self._host = host

    @property
    def port(self) -> int:
        """
        Hive port, that'll be used for Connector creating

        :return: int with port
        """
        return self._port

    @port.setter
    def port(self, port: int):
        """
        Sets new port to attribute of Connector

        :param port: new port
        """
        self._port = port

    @property
    def username(self) -> str:
        """
        Hive username, that'll be used for Connector creating

        :return: str with username
        """
        return self._username

    @username.setter
    def username(self, username: str):
        """
        Sets new username to attribute of Connector

        :param username: new username
        """
        self._username = username

    @property
    def database(self) -> str:
        """
        Hive database, that'll be used for Connector creating

        :return: str with database
        """
        return self._database

    @database.setter
    def database(self, database: str):
        """
        Sets new database to attribute of Connector

        :param port: new database
        """
        self._database = database

    @property
    def auth(self) -> str:
        """
        Hive auth, that'll be used for Connector creating

        :return: str with auth
        """
        return self._auth

    @auth.setter
    def auth(self, auth: str):
        """
        Sets new auth to attribute of Connector

        :param auth: new auth
        """
        self._auth = auth

    @property
    def configuration(self) -> dict:
        """
        Hive configuration, that'll be used for Connector creating

        :return: dict with configuration
        """
        return self._configuration

    @configuration.setter
    def configuration(self, configuration: dict):
        """
        Sets new configuration to attribute of Connector

        :param configuration: new configuration
        """
        self._configuration = configuration

    @property
    def password(self) -> str:
        """
        Hive password, that'll be used for Connector creating

        :return: str with password
        """
        return self._password

    @password.setter
    def password(self, password: str):
        """
        Sets new password to attribute of Connector

        :param password: new password
        """
        self._password = password

    @property
    def thrift_transport(self):
        """
        Hive thrift_transport, that'll be used for Connector creating

        :return: A ``TTransportBase`` with thrift_transport
        """
        return self._thrift_transport

    @thrift_transport.setter
    def thrift_transport(self, thrift_transport):
        """
        Sets new thrift_transport to attribute of Connector

        :param thrift_transport: new thrift_transport
        """
        self._thrift_transport = thrift_transport

    def create(self):
        """
        :return Connection object
        """
        from pyhive import hive

        return hive.Connection(
            host=self._host,
            port=self._port,
            username=self._username,
            database=self.database,
            auth=self._auth,
            configuration=self._configuration,
            kerberos_service_name=self._kerberos_service_name,
            password=self._password,
            thrift_transport=self._thrift_transport).cursor()
