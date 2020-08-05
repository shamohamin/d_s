from selenium import webdriver
from bs4 import BeautifulSoup
from utils.animated_loading import Loading
import time
from database.query_executer import Database
from utils.utils import (NotAuthotized, NotFoundPage,
                         PersianToEnglishConverter)
import json


class RequestHandler:
    YOUR_MARKUP = "html.parser"

    def __init__(self, db: Database, base_url=None):
        self.db, self.base_url = db, base_url
        self.browser, self.soup_content = webdriver.Chrome(), None

    def make_request(self, params=None):
        try:
            # loading = Loading("\r😃😃😃")
            # loading.start()
            self.browser.get(self.base_url)
            # loading.is_over = True
            time.sleep(1.5)
            # self.__request_log()
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

    def setup_beautiful_soup(self):
        try:
            self.soup_content = BeautifulSoup(
                self.content, RequestHandler.YOUR_MARKUP
            )
        except Exception as ex:
            print("inside setup: ", ex)

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
            self.__transfer_to_database(table_name="stocks", datas=datas)
            print("databased updated no error")
        except Exception as ex:
            print("inside url_finder: ", ex)

    def __transfer_to_database(self, table_name, datas: list):
        try:
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
                        if value['type'] == 'str':
                            query += "'{}',".format(value['value'])
                        else:
                            query += "{},".format(value['value'])
                    else:
                        if value['type'] == 'str':
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

            query = "SELECT stock_id, url FROM stocks limit {} OFFSET {};".format(
                limit_dic['limit'], limit_dic['offset'])
            self.db.execute(query=query)
            results = self.db.results
            con = PersianToEnglishConverter()
            print(results)
            time.sleep(1)
            datas = []
            for result in results:
                print("aoodododododo")
                stock_id, url = result
                self.base_url = url
                self.make_request()
                data_shcema = {
                    'persons_num_of_buyers': {
                        'value': int(con.convert(self.browser.find_elements_by_class_name('personbuyercount')[0].text)),
                        'type': 'int'
                    },
                    'company_num_of_buyers': {
                        'value': int(con.convert(self.browser.find_elements_by_class_name('companybuyercount')[0].text)),
                        'type': 'int'
                    },
                    'persons_amount_of_buy': {
                        "value": "{} {}".format(con.convert("".join(self.browser.find_elements_by_class_name('personbuyvolume')[0].text.split('٫'))), self.browser.find_elements_by_class_name('short-type-number')[0].text),
                        "type": 'str'
                    },
                    'company_amount_of_buy': {
                        "value": con.convert(self.browser.find_elements_by_class_name('companybuyvolume')[0].text),
                        "type": 'str'
                    },
                    'persons_num_of_seller': {
                        'value': con.convert(self.browser.find_elements_by_class_name('personsellercount')[0].text),
                        'type': 'int'
                    },
                    'company_num_of_seller': {
                        'value': con.convert(self.browser.find_elements_by_class_name('companysellercount')[0].text),
                        'type': 'int'
                    },
                    'persons_amount_of_sells': {
                        'value': "{} {}".format(con.convert(self.browser.find_elements_by_class_name('personsellvolume')[0].text), self.browser.find_elements_by_class_name('short-type-number')[0].text),
                        'type': 'str'
                    },
                    'company_amount_of_sells': {
                        'value': con.convert(self.browser.find_elements_by_class_name('companysellvolume')[0].text),
                        'type': 'str'
                    },
                    'stock_id': {
                        'value': stock_id,
                        'type': 'int'
                    }
                }
                print(data_shcema)
                datas.append(data_shcema)
            self.__transfer_to_database(
                table_name="stocks_comapny_person_summary", datas=datas
            )
        except Exception as ex:
            print(ex)

    def close_connection(self):
        self.browser.quit()

    def execute(self, params):
        self.make_request(params)
        self.url_finder()
        self.close_connection()

    def thread_executor(self, limit_dic):
        self.db.execute(query="DELETE FROM stocks_comapny_person_summary",
                        output_method="get_output_of_insert_and_update")
        self.company_and_trader_url_finder(limit_dic)
        self.close_connection()
