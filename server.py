import json
import time
from http.server import BaseHTTPRequestHandler,HTTPServer
from StatusPageBuilder import BasePageBuilder
from socketserver import ThreadingMixIn
import threading
controller = __import__('tradfri-lights')
status = __import__('tradfri-status')


def mapLights(groupName):
        lights = []
        groups = props.get('group')
        for id in groups.get(groupName):
                if id.isdigit():
                        lights.append(int(id))
                else:
                        lights += mapLights(id)
        return lights


def read_server_config():
    lines = open("server.cfg","r").readlines()
    readMode = ""
    properties = {'group':{},'langmap':{}}
    for line in lines:
        propLine = line.strip()
        if propLine[0] == "#":
            readMode = propLine
            continue
        if readMode == "#Server":
            serverProperty = propLine.split("=")
            properties[serverProperty[0]]=serverProperty[1]
        elif readMode == "#Groups":
            groupName = propLine.split("=")
            properties['group'][groupName[0]]=groupName[1].split("+")
        elif readMode == "#LangMap":
            langMap = propLine.split("=")
            properties['langmap'][langMap[0]]=langMap[1]
    return properties



class MyHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        self.do_HEAD()
        self.wfile.write(bytes(BasePageBuilder.build(bulb_statuses), 'UTF-8'))
        self.send_response(200)

    def do_POST(self):
        """Respond to a GET request."""
        self.do_HEAD()
        data = json.loads(self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8'))
        state = data.get('state')
        groupName = props.get('langmap').get(data.get('group').lower())
        lights = mapLights(groupName)
        # This is a brightness config, that we only want to apply to active lights
        if state.isdigit():
            state = int(state)
            lights = [light for light in lights if light in
                      [bulb.get('id') for bulb in bulb_statuses if bulb.get('brightness') > 0]]

        for light in lights:
            if state == 'off':
                controller.main(['-l',str(light), '-a', 'power', '-v',str(state)])
                [bulb for bulb in bulb_statuses if bulb.get('id') == light][0]['brightness'] = 0
            elif state == 'on':
                controller.main(['-l',str(light),'-a', 'brightness', '-v','100'])
                [bulb for bulb in bulb_statuses if bulb.get('id') == light][0]['brightness'] = 100
            # For brightness configuration
            else:
                controller.main(['-l',str(light),'-a', 'brightness', '-v',str(state)])
                [bulb for bulb in bulb_statuses if bulb.get('id') == light][0]['brightness'] = state

props = read_server_config()
hubip = props.get('hubip')
security_code = props.get('securityid')
bulb_statuses = status.getBulbInfoObject(hubip, security_code)
HOST_NAME = props.get('HOST_NAME')
PORT_NUMBER = int(props.get('PORT_NUMBER'))


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ This class allows to handle requests in separated threads.
        No further content needed, don't touch this. """

if __name__ == '__main__':
    server_class = ThreadedHTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print(time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER))

