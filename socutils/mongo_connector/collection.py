from collections import Iterable

from bson import ObjectId

from .client import Client
from .database import Database


class Collection(object):
    __connection = None

    def __init__(self, label: str, database: Database):
        """
        Object that wraps pymongo.Collection

        :param label: Collection label
        :param database: Instance of mongo_client.Database, that used for connection create
        """
        if label is None:
            raise ValueError('Label should be provided to collection')
        self._label = label
        if database is None:
            raise ValueError('Database instance should be provided to collection')
        self._database = database

    @classmethod
    def create(cls, label: str, client: Client, database_label: str = None):
        """
        Creates Collection instance with initialization of mongo_client.Database instance

        :param label: Collection label
        :param client: instance of mongo_client.Client for mongo_client.Database initialization
        :param database_label: label of Database connected to
        :return: Collection instance
        """
        return cls(label, Database(client, database_label))

    @classmethod
    def create_without_client(cls, label: str, host: str, port: int, db_label: str = None, *args, **kwargs):
        """
        Creates Collection instance from specified params

        :param label: Collection label
        :param db_label: Label of the database connected to
        :param host: MongoDB host, that'll be used for database connector creating
        :param port: MongoDB port, that'll be used for database connector creating
        :param args: additional parameters for mongo_client.Client instance creation
        :param kwargs: additional parameters for mongo_client.Client instance creation
        :return: Collection instance
        """
        return cls(label, Database.create(db_label, host, port, *args, **kwargs))

    @property
    def label(self):
        """
        Collection label

        :return: collection label
        """
        return self._label

    @label.setter
    def label(self, label: str):
        """
        Setter for mongo_client.Collection.label

        :param label: new label for collection
        """
        self.__connection = None
        self._label = label

    @property
    def database(self):
        """
        Instance of mongo_client.Database, that used for connection create

        :return: mongo_client.Database instance
        """
        return self._database

    @database.setter
    def database(self, database: Database):
        """
        Setter for mongo_client.Collection.database

        :param database: mongo_client.Database instance
        """
        self.__connection = None
        self._database = database

    def set_new_database(self, host: str, port: int, db_label: str = None, *args, **kwargs):
        """
        Creates mongo_connector.Database instance and set it to self

        :param db_label: Label of the database connected to
        :param host: MongoDB host, that'll be used for database connector creating
        :param port: MongoDB port, that'll be used for database connector creating
        :param args: additional parameters for mongo_client.Client instance creation
        :param kwargs: additional parameters for mongo_client.Client instance creation
        """
        self.__connection = None
        self._database = Database.create(db_label, host, port, *args, **kwargs)

    def get_db_collection(self, instance: str = None, label: str = None):
        """
        Method that returns pymongo.Collection that self wraps

        :param instance: Label of the database connected to
        :param label: Label of specified collection, default value: self.label
        :return:
        """
        if label is None:
            if self.__connection is None:
                self.__connection = self.database.get_instance(instance)[self.label]
            connection = self.__connection
        else:
            connection = self.database.get_instance(instance)[label]
        return connection

    def insert_one(self, document: dict, instance: str = None, *args, **kwargs):
        """
        Insert one into specified collection in mongo

        :param document: Body of document that should be inserted to
        :param instance: Label of the database connected to
        :param args: additional parameters that sent to pymongo.Collection.insert_one()
        :param kwargs: additional parameters that sent to pymongo.Collection.insert_one()
        :return: WriteResult
        """
        db_collection = self.get_db_collection(instance)
        return db_collection.insert_one(document, *args, **kwargs)

    def insert_many(self, documents: Iterable, instance: str = None, *args, **kwargs):
        """

        :param documents: Label of the database connected to
        :param instance: List of documents that should be inserted to
        :param args: additional parameters that sent to pymongo.Collection.insert_many()
        :param kwargs: additional parameters that sent to pymongo.Collection.insert_many()
        :return: List of inserted ids
        """
        if not documents:
            raise ValueError('documents should be provided to Collection.insert_many')
        if not isinstance(documents, Iterable):
            raise TypeError('documents should be not empty list')
        db_collection = self.get_db_collection(instance)

        return db_collection.insert_many(documents, *args, **kwargs)

    def find(self, query: dict = None, projection: dict = None, instance: str = None, *args, **kwargs):
        """
        Find documents that match query condition in specified collection

        :param instance: Label of the database connected to
        :param query: query conditions
        :param projection: description of fields that should be return
        :param args: additional parameters that sent to pymongo.Collection.find()
        :param kwargs: additional parameters that sent to pymongo.Collection.find()
        :return: List of documents that match search query
        """
        db_collection = self.get_db_collection(instance)
        if query is None:
            query = {}
        return db_collection.find(query, projection, *args, **kwargs)

    def find_one(self, query: dict, projection: dict = None, instance: str = None, *args, **kwargs):
        """
        Find one document that matches query condition in specified collection

        :param instance: Label of the database connected to
        :param query: query conditions
        :param projection: description of fields that should be return
        :param args: additional parameters that sent to pymongo.Collection.find_one()
        :param kwargs: additional parameters that sent to pymongo.Collection.find_one()
        :return: Document that matches search query
        """
        db_collection = self.get_db_collection(instance)
        return db_collection.find_one(query, projection, *args, **kwargs)

    def find_one_by_id(self, document_id, projection: dict = None, instance: str = None,  *args, **kwargs):
        """
        Find one document by its id in specified collection

        :param instance: Label of the database connected to
        :param document_id: id of document that should be found in specified collection
        :param projection: description of fields that should be return
        :param args: additional parameters that sent to pymongo.Collection.find_one()
        :param kwargs: additional parameters that sent to pymongo.Collection.find_one()
        :return: Document with id provided to
        """
        if document_id is None:
            raise ValueError('document_id should be provided to Collection.find_one_by_id')
        if not isinstance(document_id, ObjectId):
            document_id = ObjectId(document_id)
        return self.find_one({'_id': document_id}, projection, instance, *args, **kwargs)

    def count_documents(self, query: dict, instance: str = None, *args, **kwargs):
        """
        Count documents, that match the query, in specified collection

        :param instance: Label of the database connected to
        :param query: query conditions
        :param args: additional parameters that sent to pymongo.Collection.delete_many()
        :param kwargs: additional parameters that sent to pymongo.Collection.delete_many()
        :return: count of documents that match query
        """
        db_collection = self.get_db_collection(instance)
        return db_collection.count_documents(query, *args, **kwargs)

    def update_one(self, query: dict, update: dict, instance: str = None, *args, **kwargs):
        """
        Update one document, that matches the query, in specified collection

        :param instance: Label of the database connected to
        :param query: query conditions
        :param update: operations that should be performed for update
        :param args: additional parameters that sent to pymongo.Collection.update_one()
        :param kwargs: additional parameters that sent to pymongo.Collection.update_one()
        """
        db_collection = self.get_db_collection(instance)
        return db_collection.update_one(query, update, *args, **kwargs)

    def update_one_by_id(self, document_id, update: dict, instance: str = None, *args, **kwargs):
        """
        Update one document with provided document_id in specified collection

        :param instance: Label of the database connected to
        :param document_id: id of document that should be updated in specified collection
        :param update: operations that should be performed for update
        :param args: additional parameters that sent to pymongo.Collection.update_one()
        :param kwargs: additional parameters that sent to pymongo.Collection.update_one()
        """
        if document_id is None:
            raise ValueError('document_id should be provided to Collection.update_one_by_id')
        if not isinstance(document_id, ObjectId):
            document_id = ObjectId(document_id)
        return self.update_one({'_id': document_id}, update, instance, *args, **kwargs)

    def update_many(self, query: dict, update: dict, instance: str = None, *args, **kwargs):
        """
        Update documents, that match the query, in specified collection

        :param instance: Label of the database connected to
        :param query: query conditions
        :param update: operations that should be performed for update
        :param args: additional parameters that sent to pymongo.Collection.update_many()
        :param kwargs: additional parameters that sent to pymongo.Collection.update_many()
        """
        db_collection = self.get_db_collection(instance)
        return db_collection.update_many(query, update, *args, **kwargs)

    def delete_one(self, query: dict, instance: str = None, *args, **kwargs):
        """
        Delete one document, that matches the query, in specified collection

        :param instance: Label of the database connected to
        :param query: query conditions
        :param args: additional parameters that sent to pymongo.Collection.delete_one()
        :param kwargs: additional parameters that sent to pymongo.Collection.delete_one()
        """
        db_collection = self.get_db_collection(instance)
        return db_collection.delete_one(query, *args, **kwargs)

    def delete_many(self, query: dict, instance: str = None, *args, **kwargs):
        """
        Delete documents, that match the query, in specified collection

        :param instance: Label of the database connected to
        :param query: query conditions
        :param args: additional parameters that sent to pymongo.Collection.delete_many()
        :param kwargs: additional parameters that sent to pymongo.Collection.delete_many()
        """
        db_collection = self.get_db_collection(instance)
        return db_collection.delete_many(query, *args, **kwargs)
