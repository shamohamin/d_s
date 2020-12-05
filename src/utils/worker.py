from database.query_executer import Database as DB
from requstHandler.request_handler import RequestHandler
import math
import concurrent.futures
import time
from utils.animated_loading import Loading
from pathlib import Path
import os
from .file_parser import FileParser
from configparser import ConfigParser


class Worker:
    MAX_THREAD = 10
    def __init__(self, db: DB, base_url: str):
        self.db = db
        self.base_url = base_url
        self.dir_path = Path(os.path.dirname(__file__)).parent
        self.db_columns = {}

    def get_table_schema_and_selectors(self):
        try:
            parser = ConfigParser()
            parser.read(os.path.join(self.dir_path, 'database',
                                     'column_and_selectors.ini'))
            for table_name in parser.sections():
                self.db_columns[table_name] = {}
                items = parser.items(table_name)
                for rows in items:
                    self.db_columns[table_name][rows[0]] = {}
                    self.db_columns[table_name][rows[0]]['selectors'] = []
                    selector_type = rows[1].split(',')
                    for index, s_t in enumerate(selector_type):
                        if index == len(selector_type) - 1:
                            self.db_columns[table_name][rows[0]]['type'] = s_t
                        else:
                            self.db_columns[table_name][rows[0]]['selectors'].append(s_t)
        except Exception as ex:
            print("inside schema: ", ex)

    def run_program(self):
        # RequestHandler(self.db, self.base_url).execute()
        # self.make_threads()
        self.get_table_schema_and_selectors()
        FileParser(self.db).parse(self.db_columns)

    def make_file(self):
        print(self.dir_path)
        joined_path = os.path.join(self.dir_path, "temp")
        if not os.path.exists(joined_path):
            os.mkdir(os.path.join(self.dir_path, "temp"))

    def cleaning(self):
        joined_path = os.path.join(self.dir_path, "temp")
        if os.path.exists(joined_path):
            os.rmdir(os.path.join(self.dir_path, "temp"))

    def make_threads(self):
        query = "SELECT COUNT(*) FROM stocks"
        self.db.execute(query=query)
        all_count = int(self.db.results[0][0])
        part = math.ceil(all_count / Worker.MAX_THREAD)
        parts = []
        for index in range(Worker.MAX_THREAD):
            parts.append({
                'offset': index * part,
                'limit': part
            })
        print(parts)
        request_handlers = []
        self.make_file()
        ll = Loading("Loading ")
        ll.start()
        for index in range(Worker.MAX_THREAD):
            request_handlers.append(RequestHandler(db=self.db))

        with concurrent.futures.ThreadPoolExecutor(max_workers=Worker.MAX_THREAD) as executor:
            for index, p in enumerate(parts):
                executor.submit(request_handlers[index].thread_executor, p)
        ll.is_over = True
        del request_handlers
        # self.cleaning()
