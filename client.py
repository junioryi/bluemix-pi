import time
import os, json
import ibmiotf.application
import uuid
import Image
import base64

import picamera
import random, string
import math

from time import sleep

picture_index = 0

packet_size = 3000

client = None

##### Helper function #####

# Generate random id for a picture
def randomword(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))

# Split the picture into size 3000 and publish with json
def publishEncodedImage(encoded):
    end = packet_size
    start = 0
    length = len(encoded)
    picId = randomword(8)
    pos = 0
    no_of_packets = math.ceil(length/packet_size)
    while start <= len(encoded):
        data = {
                "data": encoded[start:end], 
                "pic_id": picId,
                "pos": pos,
                "size": no_of_packets
        }

        print "publishing packet no." + str(pos)
        client.publishEvent(
                "raspberrypi", 
                options["deviceId"], 
                "return pic", 
                "json", 
                json.JSONEncoder().encode(data)
        )
        
        end += packet_size
        start += packet_size
        pos += 1

###########################

def myCommandCallback(cmd):
    print "----- Got command -----"
    print "Event: " + cmd.event
    #print cmd.data
    global picture_index
    if cmd.event == "take picture":
        
        # Generate picture file name by index
        temp_file = './pictures/' + str(picture_index) + '.jpg'

        # Open camera and take photo
        camera = picamera.PiCamera()
        try:
            camera.start_preview()
            sleep(1)
            camera.capture(temp_file, resize=(500, 281))
            camera.stop_preview()
            pass
        finally:
            camera.close()

        # Read and encode photo
        with open(temp_file, "rb") as image:
            raw = base64.b64encode(image.read())
            print "***** packet and sending picture *****"
            publishEncodedImage(raw)
            print "***** sending picture done *****"
            picture_index += 1

    elif cmd.event == "return pic":
        data = json.loads(cmd.data)
        print "The " + str(data["pos"]) + " portion of picture."


try:
    options = ibmiotf.application.ParseConfigFile("/home/pi/device.cfg")
    options["deviceId"] = options["id"]
    options["id"] = "aaa" + options["id"]
    client = ibmiotf.application.Client(options)
    client.connect()
    client.deviceEventCallback = myCommandCallback
    client.subscribeToDeviceEvents(event="take picture") 
    client.subscribeToDeviceEvents(event="return pic")
    #client.subscribeToDeviceEvents()

    while True:
        time.sleep(1)

except ibmiotf.ConnectionException  as e:
    print e

