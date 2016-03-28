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
        if s == -1 or len(path) == s:
            return

        if path.rfind('&') != -1:
            path = path[s+1:].split('&')
        else:
            path = [path[s+1:]]

        properties = {}
        for var in path:
            property = var.split('=')
            if len(property) == 1: property.append('')
            print property
            properties[property[0]] = property[1]

        return properties


    def do_GET(self):
        pages = ['','full','info']

        url_properties = self.get_fields(self.path)
        page_len = self.path.rfind('?')
        if page_len == -1: page_len = len(self.path)
        page = self.path[1:page_len]
        print "sending %s" % page

        if page not in pages:
            print '%s rejected' % page
            self.send_response(404)
            return

        self.send_response(200)

        if page == 'info':
            self.send_header('Content-type','text/html; charset=utf-8')
            self.end_headers()

            self.wfile.write("<html><head><title></title></head><body>")
            self.wfile.write("<h1>Foxall Scanner Server</h1>")
            self.wfile.write("Attached Scanner: %s %s" % (scanner.device.model, scanner.device.name))
            self.wfile.write("<h3>Available Pages</h3>")
            self.wfile.write("<p><b>full</b> Get back a live mjpeg stream of the overall scan from the scanner</p><a href=\"/full\">/full</a>")
            self.wfile.write("<p><b>info</b> Get this page</p><a href=\"/info\">/info</a>")

            self.wfile.write("<h3>Available options</h3>")
            self.wfile.write("<p>The following options have been pulled from the scanner driver just now, some properties may not be implemented. Also some options may not be named the same as on other scanners, this is because the driver is written by many developers and they dont all keep to the same naming standards! to select one of theese options you have to put them in on the scan request, simply put in <i>http://thedomain.orip/full?option=value&option=value&option=value</i> like a standard web API </p>")
            self.wfile.write("<table border=1><tr><td><b>Property</b></td><td><b>Current setting</b></td><td><b>Constraints/Available Values</b></td></tr>")

            for item in scanner.device.options:
                try: getVal = scanner.device.options[item].value
                except: getVal = 'unknown'
                getConst = scanner.device.options[item].constraint
                if getConst == None: getConst = ''
                self.wfile.write("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (item, getVal, getConst))
            self.wfile.write("</table>")
            self.wfile.write("</body></html>")

        elif not scanner.is_scanning and page in ['full', '']:
            # Header for mpjpeg style stream
            self.send_header('Content-type','image/jpeg')
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

            scanner.img.save(self.wfile,'JPEG')


        else:
            print 'Scan in progress, this request is sent single image'
            self.send_header('Content-type','image/jpeg')
            self.end_headers()
            scanner.img.save(self.wfile,'JPEG')
        return


scanner = scanner(0)
server =  ThreadedHTTPServer(('',80),scanHandler)
server.serve_forever()
