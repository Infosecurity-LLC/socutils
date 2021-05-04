class SocUtilsException(Exception):
    pass


class SettingsFileNotExistError(SocUtilsException):
    pass


class InvalidCallStackError(SocUtilsException):
    pass


"""
    MQ Connector Exceptions
"""


class MQReceiveError(SocUtilsException):
    pass


class EventRegistrationError(SocUtilsException):
    pass


"""
    Mail Exceptions
"""


class MailException(SocUtilsException):
    pass


"""
    Events REST API Exceptions
"""


class EventsAPIException(Exception):
    pass


class EmptyDeviceError(EventsAPIException):
    pass


class EmptyOrganizationError(EventsAPIException):
    pass


class EventSendError(EventsAPIException):
    pass


class EventSearchError(EventsAPIException):
    pass


class UnknownDeviceError(EventSendError):
    pass


class ServiceIDMissedError(EventsAPIException):
    pass


class QueueIDMissedError(EventsAPIException):
    pass


class BatchOrganizationError(EventsAPIException):
    pass


"""
    Kafka Exceptions
"""


class KafkaError(Exception):
    pass


class KafkaSettingsError(KafkaError):
    pass


class KafkaProducerError(KafkaError):
    pass


class AuthSettingError(KafkaError):
    pass


class AuthError(KafkaError):
    pass


"""
    Messila Api Exceptions
"""


class MessilaApiExceptions(Exception):
    pass
