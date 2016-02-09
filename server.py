from scanner import scanner
import StringIO
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer

class scanHandler(BaseHTTPRequestHandler):


    def do_GET(self):
        # Header for mpjpeg style stream
        self.send_response(200)
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


scanner = scanner()
server = HTTPServer(('',8080),scanHandler)
server.serve_forever()
