import manage
import datetime
import time

class Timer:
    def __init__(self, time_):
        self.time_ = time_

    def Time_calculations(self):
        delta = (self.time_ - datetime.datetime.now().hour + 24) % 24 - 1
        if delta == -1:
            delta = 23
        time.sleep(delta * 60 * 60)

    def First_iter_step(self):
            if datetime.datetime.now().hour == self.time_:
                return True
            time.sleep(60)
            return False

    def Run_step(self):
            if datetime.datetime.now().hour == self.time_:
                return True
            time.sleep(60)
