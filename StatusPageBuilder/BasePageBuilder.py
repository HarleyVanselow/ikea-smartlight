from os import curdir,sep
from string import Template


def build(statuses):
    localpath = curdir + sep + "StatusPageBuilder" + sep
    body = open(localpath + "index.html").read()
    list_elem = open(localpath + "listElem.html").read()
    lights = ""
    for bulb in statuses:
        lights += Template(list_elem).substitute({'light_name':str(bulb['name']),
                                                  'light_status': str(bulb['brightness'])})
    return Template(body).substitute({'light_status': lights})
