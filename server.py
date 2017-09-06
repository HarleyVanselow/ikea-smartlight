import time
import BaseHTTPServer
import simplejson
import ConfigParser
controller=__import__('tradfri-lights')
status=__import__('tradfri-status')
def mapLights(groupName):
        lights = []
        groups = props.get('group')
        for id in groups.get(groupName):
                if id.isdigit():
                        lights.append(id)
                else:
                        lights+=mapLights(id)
        return lights
def printStatusPage(bulbInfo,outputWriter):
	page = ""
	for bulb in bulbInfo:
		page+="<p>"+str(bulb['name'])+": "+str(bulb['brightness'])+"</p><br>"
	outputWriter(page)
	
def readServerConfig():
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
props = readServerConfig()
HOST_NAME = props.get('HOST_NAME')
PORT_NUMBER = int(props.get('PORT_NUMBER'))
class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
    def do_GET(self):
	print("Received GET request")
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
	conf = ConfigParser.ConfigParser()
        conf.read('tradfri.cfg')
        hubip = conf.get('tradfri', 'hubip')
        securityid = conf.get('tradfri', 'securityid')	
	bulbStatuses = status.getBulbInfoObject(hubip,securityid)
	self.wfile.write("<html><head><title>Harley Basement Lights Status Page</title></head>")
	printStatusPage(bulbStatuses,self.wfile.write)
	print("Done retreiving status")
        self.send_response(200)
        self.end_headers()
    def do_POST(self):
        """Respond to a GET request."""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("<html><head><title>Title goes here.</title></head>")
        self.wfile.write("<body><p>This is a test.</p>")
        # If someone went to "http://something.somewhere.net/foo/bar/",
        # then s.path equals "/foo/bar/"
	self.data_string = self.rfile.read(int(self.headers['Content-Length']))

        self.send_response(200)
        self.end_headers()

        data = simplejson.loads(self.data_string)
	print(data)
	state = data.get('state')
	groupName = props.get('langmap').get(data.get('group').lower())
	groups = props.get('group')
	lights = mapLights(groupName)
	for light in lights:
		print("Light: "+light+", state:"+state)
		if state == 'off':
			controller.main(['-l',light, '-a', 'power', '-v',state])
		elif state == 'on':
			controller.main(['-l',light,'-a', 'brightness', '-v','100'])
		# For brightness configuration
		else:
			controller.main(['-l',light,'-a', 'brightness', '-v',state])
if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    print props
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
