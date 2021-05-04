import logging
import subprocess
from socutils.exceptions import AuthError, AuthSettingError
logger = logging.getLogger(__name__)


class Auth:
    def __init__(self, auth, **kwargs):
        self.params = kwargs
        self.kafka_security = None
        auth_types = {'kerberos': self.__kerberos_auth,
                      'ssl': self.__ssl_auth,
                      'anonymous': self.__anonymous_auth}

        if not auth_types.get(auth):
            raise AuthSettingError('unknown auth type')
        try:
            auth_types[auth]()
        except KeyError:
            raise AuthSettingError

    def __kerberos_auth(self):
        login = self.params['login']
        password = self.params['password']
        keytab = self.params['keytab']
        KerberosAuth(login=login, password=password, keytab=keytab)
        self.kafka_security = {'security_protocol': 'SASL_PLAINTEXT',
                               'sasl_mechanism': 'GSSAPI'}

    def __ssl_auth(self):
        ssl_keyfile = self.params['keyfile']
        ssl_certfile = self.params['certfile']
        ssl_cafile = self.params['cafile']
        ssl_check_hostname = self.params.get('check_hostname') if self.params.get('check_hostname') else False
        self.kafka_security = {'security_protocol': 'SSL',
                               'ssl_keyfile': ssl_keyfile,
                               'ssl_certfile': ssl_certfile,
                               'ssl_cafile': ssl_cafile,
                               'ssl_check_hostname': ssl_check_hostname}

    def __anonymous_auth(self):
        self.kafka_security = {}

    def get_params(self):
        return self.kafka_security


class KerberosAuth:
    def __init__(self, login, password, keytab):
        self._user = login
        self._passwd = password
        self._keytab = keytab
        self.auth()

    def auth(self):
        """
        Авторизация, приоритетно по keytab
        """
        if self._keytab:
            self._kerberos_auth_keytab()
        elif self._passwd and not self._keytab:
            self._kerberos_auth_pwd()
        else:
            logger.error('FAIL auth WTF')

    def _kerberos_auth_pwd(self, ):
        """
        Авторизация в домене по логину/паролю
        """
        kinit = '/usr/bin/kinit'
        kinit_args = [kinit, '%s' % (self._user)]
        kinit = subprocess.Popen(kinit_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        kinit.stdin.write('%s\n' % self._passwd)
        kinit.wait()

    def _kerberos_auth_keytab(self):
        """
        Авторизация в домене по ключу
        """
        comand = "/usr/bin/kinit -k -t {keytab} {user}".format(keytab=self._keytab, user=self._user)
        try:
            subprocess.check_output(comand, shell=True)
        except subprocess.CalledProcessError as err:
            raise AuthError('FAIL auth [{}] with error code [{}]'.format(err.cmd, err.returncode))
