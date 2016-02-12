from scanner import scanner
import StringIO
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn
import threading

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class scanHandler(BaseHTTPRequestHandler):


    def do_GET(self):
        self.send_response(200)
        if not scanner.is_scanning:
            # Header for mpjpeg style stream
            self.send_header('Content-type','multipart/x-mixed-replace; boundary=--frame')
            self.end_headers()

            # Begin scan, it feeds a frame at a time
            scanner.start_scan()
            while scanner.is_scanning:

                    scanner.scan()

                    #Save to IO to get length
                    tmpFile = StringIO.StringIO()
                    scanner.img.save(tmpFile,'JPEG')

                    # Each frame is sent with this header
                    self.wfile.write("--frame")
                    self.send_header('Content-type','image/jpeg')
                    self.send_header('Content-length',str(tmpFile.len))
                    self.end_headers()
                    # Send image
                    scanner.img.save(self.wfile,'JPEG')
        else:
            print 'Scan in progress, this request is sent single image'
            self.send_header('Content-type','image/jpeg')
            self.end_headers()
            scanner.img.save(self.wfile,'JPEG')
        return


scanner = scanner()
server =  ThreadedHTTPServer(('',8080),scanHandler)
server.serve_forever()
