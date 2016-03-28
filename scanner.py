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
    def __init__(self, deviceint):

        devices = pyinsane.get_devices()
        while len(devices) <= 0:
            print "Can not find scanner, retrying in 10 seconds"
            sleep(10)
            devices = pyinsane.get_devices()

        self.device = devices[deviceint]

        print "Using scanner: %s" % str(self.device.model)
        print "Address: %s" % str(self.device.name)

        self.device.options['resolution'].value = 75
        self.device.options['mode'].value = 'Color'
        if 'preview' in self.device.options.keys(): self.device.options['preview'].value = True

        self.subimg = Image.new("RGB", (1, 1), "#F00")

        self.is_scanning = False

    def start_scan(self):

        self.is_scanning = True

        self.last_line = 0


        self.scan_session = self.device.scan()
        expected_size = self.scan_session.scan.expected_size

        if 'img' not in dir(self):
            self.img = Image.new("RGB", expected_size, "#FFF")

        if self.img.size != expected_size:
            self.img = Image.new("RGB", expected_size, "#FFF")
            #self.img.resize(expected_size)

    def end_scan(self):
        self.is_scanning = False
        del self.scan_session

    def scan(self):
        try:

            self.scan_session.scan.read()
            line = self.scan_session.scan.available_lines[1]

            sys.stdout.write("progress: [%s]\r" % line)
            sys.stdout.flush()

            #if (line > self.last_line):

            #    self.subimg = self.scan_session.scan.get_image(self.last_line, line)

            #    self.img.paste(self.subimg, (0, self.last_line))

            #self.last_line = line

        except EOFError:
            sys.stdout.write("progress:[DONE]\n")
            self.img = self.scan_session.images[0]
            self.end_scan()

    def set_option(self, option, value):
        try:
            try:
                value = int(value)
            except:
                pass

            self.device.options[option].value = value
        except:
            print 'cannot set %s to %s' % (option, value)

    def max_end_scan(self):
        # Set bed to max size
        # for some reason, this only works if set just before scan session
        self.set_option('br-y', self.device.options['br-y'].constraint[1])
        self.set_option('br-x', self.device.options['br-x'].constraint[1])


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
