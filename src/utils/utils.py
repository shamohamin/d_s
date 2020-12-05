import re


class NotFoundPage(Exception):
    def __init__(self, msg="Page Not Found 404 Exception!!!!"):
        super().__init__(msg)


class NotAuthotized(Exception):
    def __init__(self, msg="not authenticated 403"):
        super().__init__(msg)


class PersianToEnglishConverter:
    def __init__(self):
        self.num_dic = {
            '۰': '0',
            '۱': '1',
            '۲': '2',
            '۳': '3',
            '۴': '4',
            '۵': '5',
            '۶': '6',
            '۷': '7',
            '۸': '8',
            '۹': '9',
            '٬': '',
            '٫': '.',
            '/': '-',
            '٪': '',
            '—': '0'
        }
        self.pattern = "|".join(map(re.escape, self.num_dic.keys()))

    def convert(self, text):
        return re.sub(self.pattern, lambda m: self.num_dic[m.group()], text)
