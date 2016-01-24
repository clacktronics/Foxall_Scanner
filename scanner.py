from os import listdir
from time import sleep
from PIL import Image
import StringIO
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer



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
        sleep(1)
        for image in self.images:
            sleep(1)
            yield image



if __name__ == "__main__":
# This is a prototype of how it might work
    class scanHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            # Make a blank black image of bed, size info can be pulled from the SANE driver
            # It could actually be the last image rather than black.
            outputImg = Image.new("RGB", (1200, 2048), "#000000")
            # Very rough simulation of the scanner
            scanner = testScanner()
            # This returns the next chunk every 1 second
            scanReturn = scanner.scan()
            # every chunk is counted so its position is known SANE actually provides X and Y in real life
            pastePos = 0

            # Header for mpjpeg style stream
            self.send_response(200)
            self.send_header('Content-type','multipart/x-mixed-replace; boundary=--frame')
            self.end_headers()

            # Begin scan, it feeds a frame at a time
            while True:
                try:
                    # load up next image chunk from scanner (this is not how it works with SANE)
                    partImage = Image.open('test_images/' + scanReturn.next())
                    # Paste it onto the output image
                    outputImg.paste(partImage, (0,pastePos))
                    # increment chunk position
                    pastePos += 102

                    #Save to IO to get length
                    tmpFile = StringIO.StringIO()
                    outputImg.save(tmpFile,'JPEG')

                    # Each frame is sent with this header
                    self.wfile.write("--frame")
                    self.send_header('Content-type','image/jpeg')
                    self.send_header('Content-length',str(tmpFile.len))
                    self.end_headers()
                    # Send image
                    outputImg.save(self.wfile,'JPEG')

                except KeyboardInterrupt:
                    break
                except:
                    print "End of Stream"
                    break
            return

    server = HTTPServer(('',8080),scanHandler)
    server.serve_forever()

    # Output image, this is a black square and the chunks are pasted into it
