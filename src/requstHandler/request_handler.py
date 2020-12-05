from selenium import webdriver
from utils.animated_loading import Loading
import time
from database.query_executer import Database
from utils.utils import (NotAuthotized, NotFoundPage,
                         PersianToEnglishConverter)
from selenium.webdriver.chrome.options import Options
import json
import os
from pathlib import Path


class RequestHandler:
    BROWSER_OPTION = Options()

    def __init__(self, db: Database, base_url=None):
        self.db, self.base_url = db, base_url
        RequestHandler.BROWSER_OPTION.headless = True
        self.browser, self.soup_content = webdriver.Chrome(
            options=RequestHandler.BROWSER_OPTION), None
        self.dir_name = Path(os.path.dirname(__file__))

    def make_request(self, params=None):
        try:
            self.browser.get(self.base_url)
            time.sleep(1.5)
        except Exception as ex:
            print(ex)

    def __request_log(self):
        logs = json.loads(self.browser.get_log('har')[0]['message'])
        for log in logs['log']['entries'][0]['response']:
            print(log)
            if log['status'] and log['status'] == 404:
                raise NotFoundPage()
            elif log['status'] and log['status'] == 403:
                raise NotAuthotized()

    def url_finder(self, params=None):
        try:
            anchors = self.browser.find_elements_by_class_name('symbol')
            datas = []
            for anchor in anchors:
                trade_url = anchor.get_attribute('href').split('/')
                ll = len(trade_url)
                trade_url = trade_url[:ll-1]
                trade_url = "/".join(trade_url)
                trade_url += "/trades"
                print(trade_url)
                data_schema = {
                    'stock_name': {
                        'value':  anchor.text,
                        'type': 'str'
                    },
                    'url': {
                        'value': anchor.get_attribute('href'),
                        'type': 'str'
                    },
                    'trade_url': {
                        'value': trade_url,
                        'type': 'str'
                    }
                }
                datas.append(data_schema)
            print("inside database inside url_finder wait")
            self.db.execute(query="DELETE FROM stocks")
            self.transfer_to_database(table_name="stocks", datas=datas)
            print("databased updated no error")
        except Exception as ex:
            print("inside url_finder: ", ex)

    def transfer_to_database(self, table_name, datas: list):
        try:
            print(datas)
            query = "INSERT INTO {} (".format(table_name)
            for index, key in enumerate(datas[0].keys()):
                if index != len(datas[0].keys()) - 1:
                    query += "{},".format(key)
                else:
                    query += "{})".format(key)
            query += " VALUES ("
            safe_len = len(query)
            for data in datas:
                query = query[:safe_len]
                for index, value in enumerate(data.values()):
                    if index != len(data.values()) - 1:    
                        if value['type'] != 'int':
                            query += "'{}',".format(value['value'])
                        else:
                            query += "{},".format(value['value'])
                    else:
                        if value['type'] != 'int':
                            query += "'{}');".format(value['value'])
                        else:
                            query += "{});".format(value['value'])
                self.db.execute(
                    query=query, output_method="get_output_of_insert_and_update"
                )
        except Exception as ex:
            print(ex)

    def company_and_trader_url_finder(self, limit_dic):
        try:
            query = "SELECT stock_id, url, trade_url FROM stocks limit {} OFFSET {};".format(
                limit_dic['limit'], limit_dic['offset'])
            self.db.execute(query=query)
            results = self.db.results
            con = PersianToEnglishConverter()
            print(results)
            time.sleep(0.3)
            for index, result in enumerate(results):
                stock_id, url, trade_url = result
                self.base_url = url
                self.make_request()
                with open(os.path.join(self.dir_name.parent, "temp", ("{}.txt".format(stock_id))), "w") as file:
                    file.write(self.browser.page_source)
                self.base_url = trade_url
                self.make_request()
                with open(os.path.join(self.dir_name.parent, "temp", ("{}_trade.txt".format(stock_id))), "w") as file:
                    file.write(self.browser.page_source)
        except Exception as ex:
            print(ex)

    def close_connection(self):
        self.browser.quit()

    def execute(self, params):
        self.make_request(params)
        self.url_finder()
        self.close_connection()

    def thread_executor(self, limit_dic):
        # self.db.execute(query="DELETE FROM stocks_comapny_person_summary",
        #                 output_method="get_output_of_insert_and_update")
        self.company_and_trader_url_finder(limit_dic)
        self.close_connection()
