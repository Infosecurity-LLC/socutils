## Описание
Описывает часто используемую и повторяющуюся функциональность в сервисах SOC.

### Settings
Получение настроек из заданного файла (по умолчанию data/setting.yaml)

```python
setting = socutils.get_settings()
```

### EventsApiClient
Взаимодействие с OTRS REST API.  

```python
events_client = socutils.EventsAPIClient(
    '127.0.0.1', api_port=5000, organization='other', device='test', ssl=False)
print(ec.status)
events_client.send_event({"name": "Ivan Petrovich", "desc": "something's going on"})
```

### MailSender
Отправка почтовых уведомлений.  

```python
mail_sender = socutils.mail.MailSender(server, port, username, passwd, ssl, login)
mail_sender.send_msg(
    'sender@example.org.corp', 
    ['recipient1@example.org.corp', 'recipient2@example.org.corp'], 
    'Cat Pictures Subject', 
    'Have you seen it?', 
    attachments=['funny_cat.jpg'], 
    from_='Me')
```

### KafkaConnector
Доступно две обертки над libkafka  
confluent-kafka и python-kafka  
для работы через python-kafka используем kafkaconn.kafkaconnector  
для confluent-kafka kafkaconn.confluentkafka  
 
Все примеры с python-kafka  


## Auth
Поддерживаются типы аутентификации:  
anonymous  
kerberos  
ssl_cert  
Для анонимной авторизации ```auth = kafkaconn.auth.Auth(auth='anonymous')```
## Пример конфигурации 
```yaml
kafka:
  group_id: test_group_id
  topics:
    - topic_name
  servers:
    - kafka0.corp:6667
    - kafka1.corp:6667
    - kafka2:6667
#### Kerberos
  auth_type: kerberos
  auth_params:
    login: user@org.corp
    password:
    keytab: /home/user/user.keytab

#### SSL
  auth_type: ssl
  auth_params:
    keyfile: data/keyname.key
    certfile: data/keyname.crt
    cafile: data/ca.crt
```


## ConsumerExample
```python
from socutils import kafkaconn
auth = kafkaconn.auth.Auth(auth=setting['kafka']['auth_type'],
                           **setting['kafka']['auth_params'])
consumer = kafkaconn.kafkaconnector.Consumer(servers=setting['kafka']['servers'],
                                             group_id=setting['kafka']['group_id'],
                                             topics=setting['kafka']['topics'],
                                             enable_auto_commit=False,
                                             auth_params=auth.get_params())
consumer.create_consumer()
for message in consumer.read_topic():
   logger.info('Skip alert topic={} part={} offset={} key={} value={}'.format(message.topic, message.partition, message.offset, message.key, message.value))
   consumer.consumer.commit()
```
## ProducerExample
```python
from socutils import kafkaconn
auth = kafkaconn.auth.Auth(auth=setting['kafka']['auth_type'],
                           **setting['kafka']['auth_params'])
consumer = kafkaconn.kafkaconnector.Consumer(servers=setting['kafka']['servers'],
                                             group_id=setting['kafka']['group_id'],
                                             topics=setting['kafka']['topics'],
                                             enable_auto_commit=False,
                                             auth_params=auth.get_params())
                                             
producer = kafkaconn.kafkaconnector.Producer(servers=setting['kafka']['servers'],auth_params=auth.get_params())
producer.create_producer()
producer.send_json_callback('topic_name', {'exkey': 'exvals'})
producer.flush()
```


### Log
Упрощение инициализации логгеров и добавления лог хендлеров.  

```python
socutils.log.add_file_handler(logger, '/var/log/log_path', logging.INFO)
```

## Hive connector

### System-wide requirements

- libsasl2-dev
- g++

Нужны для сборки зависимостей для pyhive

### Python requirements
 
 Python version: 3.6
 
 Dependencies provided in [hive_connector/requirements.txt]
- sasl >= 0.2.1
- thrift >= 0.11.0
- thrift_sasl >= 0.3.0
- pyhive[hive] >= 0.6.1


## Установка
```python3 setup.py install```

Для работы mqconnector необходимо дополнительно установить pyzmq

