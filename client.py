import time
import os, json
import ibmiotf.application
import uuid

client = None

def myCommandCallback(cmd):
    print "----- Got command -----"
    print cmd.event
    print cmd.data

try:
    options = ibmiotf.application.ParseConfigFile("/home/pi/device.cfg")
    options["deviceId"] = options["id"]
    options["id"] = "aaa" + options["id"]
    client = ibmiotf.application.Client(options)
    client.connect()
    client.deviceEventCallback = myCommandCallback
    # It will got all publish event unless add argument event="some event".
    client.subscribeToDeviceEvents() 

    while True:
        myData = {'Data 1' : True, 'Data 2' : False}
        client.publishEvent("raspberrypi", options["deviceId"], "Test event", "json", myData)
        time.sleep(5)

except ibmiotf.ConnectionException  as e:
    print e

