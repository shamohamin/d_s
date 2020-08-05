import time
import sys
import threading
import math


class Loading(threading.Thread):
    def __init__(self, text):
        self.text = text
        self.is_over = False
        threading.Thread.__init__(self)

    def run(self):
        self.animated_text()
        return

    def make_time(self, sec_count):
        text = ""
        sec = sec_count % 60
        minute = math.floor(sec_count / 60)
        hour = math.floor(sec_count / 3600)
        if len(str(hour)) !=  2:
            text += "0{}:".format(hour)
        else:
            text += "{}".format(hour)
        if len(str(minute)) != 2:
            text += "0{}:".format(minute)
        else:
            text += "{}".format(minute)
        if len(str(sec)) != 2:
            text += "0{}".format(sec)
        else:
            text += "{}".format(sec)
        return text
        
    def make_loading(self, spent_time):
        sys.stdout.write('\rspented_time: {}'.format(spent_time))
        sys.stdout.flush()
        
    def animated_text(self):
        count = 0
        while True:
            if self.is_over:
                break            
            time.sleep(1)
            count += 1
            self.make_loading(self.make_time(int(count)))