import os
from pathlib import Path
import glob
from bs4 import BeautifulSoup
import re
from .utils import PersianToEnglishConverter as PE
import sys
from requstHandler.request_handler import RequestHandler
from database.query_executer import Database as DB


class FileParser:
    YOUR_MARKUP = "html.parser"
    CONVERTER = PE()

    def __init__(self, db: DB, file_format="txt", temp_dir_file="temp"):
        self.file_format, self.soup_content, self.content = file_format, None, None
        self.db = db
        self.temp_folder = os.path.join(
            Path(os.path.dirname(__file__)).parent, temp_dir_file)
        self.reHandler = RequestHandler(db=self.db)
        self.__check_file()

    def __check_file(self):
        if not os.path.exists(self.temp_folder):
            raise FileNotFoundError

    def __setup_beautiful_soup(self):
        try:
            self.soup_content = BeautifulSoup(
                self.content, FileParser.YOUR_MARKUP
            )
        except Exception as ex:
            print("inside setup: ", ex)

    def __make_select_by_class(self, columns, selectors, data_types, file_name: str):
        data_shecma = {}
        try:
            for index, col in enumerate(columns):
                if re.search('(_id)$', col):
                    data_shecma[col] = {
                        'value':  int(''.join(file_name.split('/')[-1][0: file_name.split('/')[-1].find('.')])),
                        'type': 'int'
                    }
                    continue

                value_selected = []
                for select in selectors[index]:
                    value_selected.append(FileParser.CONVERTER.convert(
                        text=self.soup_content.find(class_=select).text))

                data_shecma[col] = {
                    'type': data_types[index],
                    'value': ''.join(value_selected)
                }
            print(data_shecma)
        except Exception as ex:
            print('inside __make_select_by_class: ', ex)

        return data_shecma

    def __make_select_by_table(self, columns, selectors, data_types, file_name: str):
        data_schemas = []
        try:
            table = self.soup_content.find(id="DataTables_Table_0")
            table_rows = table.find('tbody').find_all('tr')
            print(len(table_rows))
            
            for row in table_rows:
                tds, data_schema = row.find_all('td'), {}
                for index, col in enumerate(columns):
                    if re.search('(_id)$', col):
                        data_schema[col] = {
                            'value':  int(''.join(file_name.split('/')[-1][0: file_name.split('/')[-1].find('_')])),
                            'type': 'int'
                        }
                        continue

                    value_selected = []
                    for select in selectors[index]:
                        value_selected.append(FileParser.CONVERTER.convert(
                            text=tds[int(select)].text))
                    value = ''.join(value_selected).strip()
                    data_schema[col] = {
                        'value': value,
                        'type': data_types[index]
                    }
                print(data_schema)
                data_schemas.append(data_schema)
        except SystemExit:
            print("exit work as spected!!!!")
        except Exception as ex:
            print('inside __make_select_by_table: ', ex)
        finally:
            return data_schemas

    def __make_table(self, files, table_name, table_schema: dict):
        columns, selectors, types, datas = [], [], [], []
        for key, value in table_schema[table_name].items():
            columns.append(key)
            selectors.append(value['selectors'])
            types.append(value['type'])

        print(columns)
        for file in files:
            with open(file, "r") as url_file:
                self.content = url_file.read()
                self.__setup_beautiful_soup()
            if not re.search("((_trade).{})$".format(self.file_format), file):
                datas.append(self.__make_select_by_class(
                    columns, selectors, types, file))
            else:
                datas.extend(self.__make_select_by_table(
                    columns, selectors, types, file))
        self.reHandler.transfer_to_database(table_name, datas)

    def parse(self, table_shecma: dict):
        files = glob.glob(self.temp_folder + "/*.{}".format(self.file_format))
        trade_url_files, url_files = [], []

        for file in files:
            if re.search('/([0-9]*((?!_trade)).{})'.format(self.file_format), file):
                url_files.append(file)
            else:
                trade_url_files.append(file)
        print(url_files)
        
        files = [url_files, trade_url_files]
        for index, table_name in enumerate(table_shecma.keys()):
            self.__make_table(files[index], table_name, table_shecma)
