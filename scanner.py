from PIL import Image
import pyinsane.abstract as pyinsane
from time import sleep
import sys

class scanner():
    '''
    This class combines pyinsane abstract and image so the scanner automatically
    produces an iterating image of the scan frame by frame. It overlays the new
    image ontop of the old.
    '''
    def __init__(self):

        devices = pyinsane.get_devices()
        while len(devices) < 0:
            print "Can not find scanner, retrying in 10 seconds"
            sleep(10)
            devices = pyinsane.get_devices()

        self.device = devices[0]

        print "Using scanner: %s" % str(self.device.model)
        print "Address: %s" % str(self.device.name)

        self.device.options['resolution'].value = 75
        self.device.options['mode'].value = 'Color'
        if 'preview' in self.device.options.keys(): self.device.options['preview'].value = True

        self.is_scanning = False

    def start_scan(self):

        self.is_scanning = True

        self.last_line = 0
        # Set bed to max size
        # for some reason, this only works if set just before scan session
        self.device.options['br-y'].value = self.device.options['br-y'].constraint[1]
        self.device.options['br-x'].value = self.device.options['br-x'].constraint[1]

        self.scan_session = self.device.scan()
        expected_size = self.scan_session.scan.expected_size

        if 'img' not in dir(self):
            self.img = Image.new("RGB", expected_size, "#FFF")

    def end_scan(self):
        self.is_scanning = False
        del self.scan_session

    def scan(self):
        try:

            self.scan_session.scan.read()
            line = self.scan_session.scan.available_lines[1]

            sys.stdout.write("progress: [%s]\r" % line)
            sys.stdout.flush()

            if (line > self.last_line):

                subimg = self.scan_session.scan.get_image(self.last_line, line)

                self.img.paste(subimg, (0, self.last_line))

            self.last_line = line

        except EOFError:
            sys.stdout.write("progress:[DONE]\n")
            self.end_scan()


if __name__ == '__main__':

    scanner = scanner()

    scanner.start_scan()
    while scanner.is_scanning:
        scanner.scan()
        scanner.img.show()

    scanner.start_scan()
    while scanner.is_scanning:
        scanner.scan()
        scanner.img.show()

















# def makeScan(device, showInfo=True):
#
#     print("I'm going to use the following scanner: %s" % (str(device.model)))
#
#     device.options['resolution'].value = 75
#     device.options['mode'].value = 'Color'
#     device.options['preview'].value = True
#     device.options['br-y'].value = device.options['br-y'].constraint[1]
#     device.options['br-x'].value = device.options['br-x'].constraint[1]
#
#
#
#     if showInfo:
#         for option in device.options:
#             constraints = device.options[option].constraint
#             if constraints != None:
#                 try: optVal = device.options[option].value
#                 except: optVal = ''
#                 print "%s : [%s] set: %s" % (option, ','.join([str(x) for x in constraints]), optVal)
#
#         print device.options.keys()
#
#
#     scan_session = device.scan()
#     try:
#         while True:
#             scan_session.scan.read()
#     except EOFError:
#         pass
#
#     image = scan_session.images[0]
#
#     image.show()
#
#
# if __name__ == '__main__':
#     from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
#     import pyinsane.abstract_th as pyinsane
#     import thread
#
#
#     import pyinsane.abstract as pyinsane
#
#     devices = pyinsane.get_devices()
#     assert(len(devices) > 0)
#
#     thread.start_new_thread( makeScan, (devices[0], True ) )
#
#     while True:
#         pass
