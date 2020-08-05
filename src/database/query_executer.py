from configparser import ConfigParser
import os
import psycopg2
import threading


class Executor:
    def config_parser(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

    def qeury_maker(self, query=None):
        raise NotImplementedError


class Database(Executor):
    config_sections = ["postgresql_conn_data"]

    def __init__(self, config_file='database.ini', query=None):
        self.config_file = config_file
        self.query, self.results = query, None
        self.db = {}
        self.connection, self.cur = None, None
        self._lock = threading.Lock()
        self.output_method_dic = {
            'get_output_of_insert_and_update': self.get_output_of_insert_and_update,
            'get_all_outputs': self.get_all_outputs
        }

    def config_parser(self):
        parser = ConfigParser()
        try:
            parser.read(os.path.join('database', self.config_file))
            if parser.has_section(Database.config_sections[0]):
                params = parser.items(Database.config_sections[0])
                for param in params:
                    self.db[param[0]] = param[1]
            else:
                raise Exception("doest have such section")
        except FileNotFoundError as fileEx:
            print("file not exists")
        except Exception as ex:
            print(ex)

    def connect_to_database(self):
        try:
            if self.connection is None:
                self.connection = psycopg2.connect(**self.db)
            else:
                raise Exception("already connection exists !!!!")
        except (Exception, psycopg2.DatabaseError) as error:
            print("inside connect method: ", error)

    def close_connection(self):
        try:
            if self.connection is not None:
                self.cur.close()
                self.connection.close()
                self.connection = None
                self.cur = None
            else:
                raise Exception("connection is None !!!!")
        except (Exception, psycopg2.DatabaseError) as error:
            print("inside close_connection: ", error)

    def execute_query(self, values=None):
        try:
            if self.query:
                try:
                    self.cur = self.connection.cursor()
                    if values is not None:
                        self.cur.execute(self.query, values)
                    else:
                        self.cur.execute(self.query)
                    self.connection.commit()
                except psycopg2.OperationalError as ex:
                    print(ex)
            else:
                raise Exception("query not provided!!!!!")
        except Exception as ex:
            print("inside execute_query: ", ex)

    def qeury_maker(self, query=None):
        try:
            if query:
                self.query = query
            else:
                raise Exception("query not provided!!!!!")
        except Exception as ex:
            print("inside query maker: ", ex)

    def execute_query_from_file(self, file):
        joined_file = os.path.join('database', file)
        print(joined_file)
        try:
            if os.path.exists(joined_file):
                print("exists")
                try:
                    self.cur = self.connection.cursor()
                    with open(joined_file, "r") as sql_file:
                        query = sql_file.read()
                        self.cur.execute(query)
                    self.connection.commit()
                    print("everyting is ok")
                except psycopg2.OperationalError as ex:
                    print(ex)
            else:
                raise Exception("file not exists")
        except (Exception, psycopg2.OperationalError) as ex:
            print("inside execute from file : ", ex)

    def get_output_of_insert_and_update(self):
        try:
            if self.cur is not None:
                rows = self.cur.rowcount
                self.results = rows
        except Exception as ex:
            print('get_output_of_insert_and_update: ', ex)

    def get_all_outputs(self):
        try:
            if self.cur is not None:
                rows = self.cur.fetchall()
                self.results = rows
            else:
                raise Exception("cursor was not provided")
        except Exception as ex:
            print("inside get all output: ", ex)

    def execute(self, query=None, file=None, values=None, output_method=None):
        with self._lock:
            self.config_parser()
            self.connect_to_database()
            if file is not None:
                self.execute_query_from_file(file)
            else:
                self.qeury_maker(query)
                self.execute_query(values=values)
            if output_method is None:
                self.get_all_outputs()
            else:
                self.output_method_dic[output_method]()
            self.close_connection()
