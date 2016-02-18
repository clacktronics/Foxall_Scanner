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
        pages = ['','full', 'line', 'stored', 'readopt']

        url_properties = self.get_fields(self.path)
        page_len = self.path.rfind('?')
        if page_len == -1: page_len = len(self.path)
        page = self.path[1:page_len]
        print "sending %s" % page

        if page not in pages:
            print '%s rejected' % page
            return

        self.send_response(200)

        if page == '':
            self.send_header('Content-type','text/html; charset=utf-8')
            self.end_headers()

            self.wfile.write("<html><head><title></title></head><body>")
            self.wfile.write("<h1>Foxall Scanner Server</h1>")
            self.wfile.write("Attached Scanner: %s %s" % (scanner.device.model, scanner.device.name))
            self.wfile.write("<h3>Available Pages</h3>")
            self.wfile.write("<p><b>full</b> Get back a live mjpeg stream of the overall scan from the scanner</p><a href=\"/full\">/full</a>")
            self.wfile.write("<p><b>line</b> Get back a live mjpeg stream of the last scanned line from the scanner</p><a href=\"/line\">/line</a>")
            self.wfile.write("<p><b>stored</b> Get back still image of last scan</p><a href=\"/stored\">stored</a>")
            self.wfile.write("<p><b>readopt</b> Get back a value of an option, you can use this to read buttons and other devices on the scanner, use options table below you may find options like 'email' or 'scan' that are buttons on the front of the scanner</p><a href=\"readopt?scan\">/readopt?scan</a>")

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
            self.wfile.write("<h3>Current Image in buffer</h3>")
            self.wfile.write("<img src=\"/stored\" width=\"300\" />")
            self.wfile.write("</body></html>")

        if page == "readopt":

            self.send_header('Content-type','text/html; charset=utf-8')
            self.end_headers()

            # only first propery
            for property in url_properties.keys():
                try: getVal = scanner.device.options[property].value
                except: getVal = 'error'
                self.wfile.write(getVal)
                break



        elif not scanner.is_scanning and page in ['full', 'line']:
            # Header for mpjpeg style stream
            self.send_header('Content-type','multipart/x-mixed-replace; boundary=--frame')
            self.end_headers()



            if url_properties != None:

                if 'composite' in url_properties.keys():
                    try:scanner.make_composite = int(url_properties['composite'])
                    except: print "error changing composite mode"
                    del url_properties['composite']

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
                    if page == 'full':
                        scanner.img.save(self.wfile,'JPEG')
                    elif page == 'line':
                        scanner.subimg.save(self.wfile,'JPEG')

        else:
            print 'Sent preview'
            self.send_header('Content-type','image/jpeg')
            self.end_headers()
            scanner.img.save(self.wfile,'JPEG')
        return


scanner = scanner(0)
server =  ThreadedHTTPServer(('',80),scanHandler)
server.serve_forever()
