#!/usr/bin/env python

# file        : tradfri-status.py
# purpose     : getting status from the Ikea tradfri smart lights
#
# author      : harald van der laan
# date        : 2017/04/10
# version     : v1.1.0
#
# changelog   :
# - v1.1.0      refactor for cleaner code                               (harald)
# - v1.0.0      initial concept                                         (harald)

"""
    tradfri-status.py - getting status of the Ikea Tradfri smart lights

    This module requires libcoap with dTLS compiled, at this moment there is no python coap module
    that supports coap with dTLS. see ../bin/README how to compile libcoap with dTLS support
"""

# pylint convention disablement:
# C0103 -> invalid-name
# C0200 -> consider-using-enumerate
# pylint: disable=C0200, C0103

from __future__ import print_function

import sys
import time
import configparser

import math

from tradfri import tradfriStatus

def main():
    """ main function """
    conf = configparser.ConfigParser()
    conf.read('tradfri.cfg')

    hubip = conf.get('tradfri', 'hubip')
    securityid = conf.get('tradfri', 'securityid')

    lightbulb = []
    lightgroup = []

    print('[ ] Tradfri: acquiring all Tradfri devices, please wait ...')
    groups = tradfriStatus.tradfri_get_groups(hubip, securityid)

    lightbulb = getBulbInfo(hubip, securityid)

    # sometimes the request are to fast, the will decline the request (flood security)
    # in this case you could increse the sleep timer
    time.sleep(.5)

    for groupid in range(len(groups)):
        lightgroup.append(tradfriStatus.tradfri_get_group(hubip, securityid,
                                                          str(groups[groupid])))

    print('[+] Tradfri: device information gathered')
    print('===========================================================\n')

    for _ in range(len(lightbulb)):
        try:
            if lightbulb[_]["3311"][0]["5850"] == 0:
                print('bulb ID {}, name: {}, brightness: {}, state: off'
                      .format(lightbulb[_]["9003"], lightbulb[_]["9001"],
                              lightbulb[_]["3311"][0]["5851"]))
            else:
                print('bulb ID {}, name: {}, brightness: {}, state: on'
                      .format(lightbulb[_]["9003"], lightbulb[_]["9001"],
                              lightbulb[_]["3311"][0]["5851"]))
        except KeyError:
            # device is not a lightbulb but a remote control, dimmer or sensor
            pass

    print('\n')

    for _ in range(len(lightgroup)):
        if lightgroup[_]["5850"] == 0:
            print('group ID: {}, name: {}, state: off'
                  .format(lightgroup[_]["9003"], lightgroup[_]["9001"]))
        else:
            print('group ID: {}, name: {}, state: on'
                  .format(lightgroup[_]["9003"], lightgroup[_]["9001"]))


def getBulbInfoObject(hubip, securityid):
    bulbs = getBulbInfo(hubip, securityid)
    bulbObject = []
    for bulb in bulbs:
        try:
            bulbProperties = {}
            bulbProperties['id'] = bulb["9003"]
            # Normalize to 0-100 scale for reporting
            bulbProperties['brightness'] = 0 if bulb["3311"][0]["5850"] == 0 else math.ceil(bulb["3311"][0]["5851"]/2.55)
            bulbProperties['name'] = bulb["9001"]
            bulbObject.append(bulbProperties)
        except KeyError:
            pass
    return bulbObject


def getBulbInfo(hubip, securityid):
    devices = tradfriStatus.tradfri_get_devices(hubip, securityid)
    lightbulb = []
    for deviceid in range(len(devices)):
        lightbulb.append(tradfriStatus.tradfri_get_lightbulb(hubip, securityid, str(devices[deviceid])))
    return lightbulb


if __name__ == "__main__":
    main()
    sys.exit(0)
