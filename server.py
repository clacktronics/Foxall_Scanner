from scanner import scanner
import StringIO
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn
import threading

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class scanHandler(BaseHTTPRequestHandler):

    def get_fields(self, path):

        s = path.rfind('?')
        if s == -1:
            return

        path = path[s+1:].split('&')

        properties = {}
        for var in path:
            property = var.split('=')
            print property
            properties[property[0]] = property[1]

        return properties


    def do_GET(self):
        pages = ['','full', 'line']

        url_properties = self.get_fields(self.path)
        page_len = self.path.rfind('?')
        if page_len == 0: page_len = len(page)+1
        page = self.path[1:]

        if page not in pages:
            print '%s rejected' % page
            return

        self.send_response(200)

        if not scanner.is_scanning:
            # Header for mpjpeg style stream
            self.send_header('Content-type','multipart/x-mixed-replace; boundary=--frame')
            self.end_headers()

            if url_properties != None:
                for property in url_properties:
                    scanner.set_option(property, url_properties[property])

                if 'br-x' not in url_properties.keys() and 'br-y' not in url_properties.keys():
                    scanner.max_end_scan()
            else:
                scanner.max_end_scan()

            print page

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
                    if page == '' or page == 'full':
                        scanner.img.save(self.wfile,'JPEG')
                    elif page == 'line':
                        scanner.subimg.save(self.wfile,'JPEG')

        else:
            print 'Scan in progress, this request is sent single image'
            self.send_header('Content-type','image/jpeg')
            self.end_headers()
            scanner.img.save(self.wfile,'JPEG')
        return


scanner = scanner(0)
server =  ThreadedHTTPServer(('',80),scanHandler)
server.serve_forever()
