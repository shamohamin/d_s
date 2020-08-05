from database.query_executer import Database as DB
from requstHandler.request_handler import RequestHandler
import math
import concurrent.futures
import time
from utils.animated_loading import Loading

class Worker:
    MAX_THREAD = 5

    def __init__(self, db: DB, base_url: str):
        self.db = db
        self.base_url = base_url

    def run_program(self):
        # RequestHandler(self.db, self.base_url).execute()
        self.make_threads()

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
        request_handlers = []
        
        ll = Loading("Loading ")
        ll.start()
        for index in range(Worker.MAX_THREAD):
            request_handlers.append(RequestHandler(db=self.db))
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=Worker.MAX_THREAD) as executor:
            for index, p in enumerate(parts):
                executor.submit(request_handlers[index].thread_executor, p)
        ll.is_over = True
        
        del request_handlers

