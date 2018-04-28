import time

from Controller import Controller
from ReadFile import ReadFile
from Model import Model
from View import View
from Parser import Parser


def Main():
    c = Controller()
    v = View(c)
    v.start()


if __name__ == '__main__':
    Main()
