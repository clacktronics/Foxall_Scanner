from os import listdir
from time import sleep

class scanner(object):
    @property
    def scanMode(self):
        return self.mode

    @scanMode.setter
    def mode(self, mode):
        pass


class saneScanner(scanner):
    pass


class testScanner(scanner):
    def __init__(self):
        self.images = [img for img in listdir('test_images') if img[0] != '.']

    def scan(self):
        for img in self.images:
            sleep(1)
            yield img



if __name__ == "__main__":

    scanner = testScanner()
    for item in  scanner.scan():
       print item
