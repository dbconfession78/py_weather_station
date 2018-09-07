import threading;
from threading import Thread;
from time import sleep

class Timer:
    def __init__(self, duration):
        self.is_counting = False
        self.__duration = duration

    @property
    def duration(self):
        return self.__duration

    @duration.setter
    def duration(self, duration):
        self.__duration = duration

    def start_timer(self):
        def run():
            self.is_counting = True
            while (self.duration > 0):
                sleep(1)
                self.duration -= 1
                # print(self.duration)
            self.is_counting = False
        timer = Thread(target=run)
        timer.start()