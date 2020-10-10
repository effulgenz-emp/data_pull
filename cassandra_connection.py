''' This module is used to connect the cassandra database

class       : CassandraCluster
functions   : cassandra_session (Creates session for the given credentials)
              pandas_result_set (returns pandas df for the given query)
              cluster_shutdown (close the connection)
'''
# Created on: Oct 10 2020
# @author: Nagaraj

import base64
import logging.config

import pandas as pd
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy

logger = logging.getLogger(__name__)


class CassandraCluster:
    '''CassandraCluster for cassandra operations like
        create connection, execute query, close connections etc.

    Attributes
    ----------
    ip_address (str): IP address of cassandra server
    port (int): Port number to connect cassandra server
    user (str): Username to connect cassandra server
    pwd (str): Encoded password to connect cassandra server

    Methods
    -------
    cassandra_cluster(self)
        Connects to cassandra cluster

        Returns:
            cluster object: Connects cassandra server
                                based on the object parameters
                                and returns cassandra cluster object


    cassandra_session(cluster, keyspace)
        Creates cassandra cluster session for the given keyspace and cluster

        Args:
            cluster (cluster object): Cassandra cluster object for
                                            the cassandra server
            keyspace (str): Keyspace value (Database)

        Returns:
            session object: Returns session object for the given keyspace


    query_result_set_to_pandas(session, query)
        Creates result set as pandas dataframe for the given query

        Args:
            session (cassandra session object): Session object for the keyspace
            query (str): Query to be executed on cassandra server

        Returns:
            dataframe: Result set as pandas dataframe


    query_result_set_to_file(self, session, query, file_location,
                                 file_type='parquet')
        Writes the result set into a file (Parquet or csv)

        Args:
            session (cassandra session object): Session object for the keyspace
            query (str): Query to be executed on cassandra server
            path (str): Folder location for the file to be saved
            filename (str): Name of the fileau
            file_type (str, optional): Extension of file. Defaults to 'parquet'


    cluster_shutdown(self, cluster)
        Shutdown the cassandra cluster

        Args:
            cluster (cassandra cluster object): Cassandra cluster object for
                                                        the cassandra server

    '''

    def __init__(self, ip_address, port, user, pwd):
        '''Constructs all necessary attributes for cassandra connection

        Args:
            ip_address (str): IP address of cassandra server
            port (int): Port number to connect cassandra server
            user (str): Username to connect cassandra server
            pwd (str): Encoded password to connect cassandra server
        '''
        self.logger = logging.getLogger(__name__)
        self.ip_address = ip_address
        self.port = port
        self.user = user
        self.pwd = pwd
        self.cluster = None
        self.logger.debug(self)

    def __enter__(self):
        auth_provider = PlainTextAuthProvider(
            username=self.user, password=base64.b64decode(self.pwd).decode())

        self.cluster = Cluster(contact_points=[self.ip_address],
                               load_balancing_policy=DCAwareRoundRobinPolicy(
            local_dc='datacenter1'),
            port=self.port, auth_provider=auth_provider,
            control_connection_timeout=100, protocol_version=3)

        self.logger.debug(self.cluster)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.cluster.is_shutdown:
            self.cluster.shutdown()

    def cassandra_cluster(self):
        '''Connects to cassandra cluster

        Returns:
            cluster object: Connects cassandra server
                                based on the object parameters
                                and returns cassandra cluster object
        '''
        auth_provider = PlainTextAuthProvider(
            username=self.user, password=base64.b64decode(self.pwd).decode())

        cluster = Cluster(contact_points=[self.ip_address],
                          load_balancing_policy=DCAwareRoundRobinPolicy(
                              local_dc='datacenter1'),
                          port=self.port, auth_provider=auth_provider,
                          control_connection_timeout=100, protocol_version=3)

        self.logger.debug(cluster)

        return cluster

    @staticmethod
    def cassandra_session(cluster, keyspace):
        '''Creates cassandra cluster session for the given keyspace and cluster

        Args:
            cluster (cluster object): Cassandra cluster object for
                                            the cassandra server
            keyspace (str): Keyspace value (Database)

        Returns:
            session object: Returns session object for the given keyspace
        '''

        session = cluster.connect()
        session.set_keyspace(keyspace)
        logger.info('Cassandra connection is established.')
        return session

    @staticmethod
    def query_result_set_to_pandas(session, query):
        '''Creates result set as pandas dataframe for the given query

        Args:
            session (cassandra session object): Session object for the keyspace
            query (str): Query to be executed on cassandra server

        Returns:
            dataframe: Result set as pandas dataframe
        '''
        # Reference:
        # https://groups.google.com/a/lists.datastax.com/g/python-driver-user/c/1v-KHtyA0Zs
        # https://www.thetopsites.net/article/59318754.shtml

        def pandas_factory(colnames, rows):
            return pd.DataFrame(rows, columns=colnames)

        session.row_factory = pandas_factory
        session.default_fetch_size = None

        result = session.execute(query, timeout=None)
        dataframe = result._current_rows

        return dataframe

    def query_result_set_to_file(self, session, query, file_location,
                                 file_type='parquet'):
        '''Writes the result set into a file (Parquet or csv)

        Args:
            session (cassandra session object): Session object for the keyspace
            query (str): Query to be executed on cassandra server
            path (str): Folder location for the file to be saved
            filename (str): Name of the fileau
            file_type (str, optional): Extension of file. Defaults to 'parquet'
        '''

        dataframe = self.query_result_set_to_pandas(session, query)
        if file_type == 'parquet':
            dataframe.to_parquet(f'{file_location}.parquet', index=False)
            self.logger.debug(f'File - {file_location}.parquet is saved')
        elif file_type == 'csv':
            dataframe.to_csv(f'{file_location}.csv', index=False)
            self.logger.debug(f'File - {file_location}.csv is saved')
        else:
            self.logger.info(f'File type - {file_type} is not allowed')

    def cluster_shutdown(self, cluster):
        '''Shutdown the cassandra cluster

        Args:
            cluster (cassandra cluster object): Cassandra cluster object for
                                                        the cassandra server
        '''
        if not cluster.is_shutdown:
            cluster.shutdown()
            self.logger.info('Cassandra cluster is shutdown')

    def __repr__(self):
        return f'''CassandraCluster('{self.ip_address}', {self.port},
                                        '{self.user}', '{self.pwd}')'''
