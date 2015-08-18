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
from PIL import Image

picture_index = 0
packet_size = 3000

# save the returning pictures
pictures = {}
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

def reconstructPicture(chuck):
    # 
    name  = chuck["pic_id"]
    pos   = chuck["pos"]
    data  = chuck["data"]
    num_p = int(chuck["size"])

    # Create image dict if first time receive this image
    if not pictures.has_key( name ):
        pictures[ name ] = {
                "count": 0,
                "total": num_p,
                "pieces": {},
                "pic_id": name
        }
        # save part of image in pieces at "pos"
        pictures[ name ]["pieces"][ pos ] = data
    else:
        # Not the first time receive this image
        pictures[ name ]["pieces"][ pos ] = data
        pictures[ name ]["count"] += 1

        if pictures[ name ]["count"] == num_p:
            print num_p
            raw = ''.join(
                    pictures[ name ]["pieces"][ part ] for part in range(num_p+1)
            )
            with open("temp_img.png", "wb") as image_file:
                #img_str = base64.b64encode(image_file.read())
                image_file.write(raw.decode('base64'))
            im = Image.open("temp_img.png")
            im.show()






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
        reconstructPicture(data)


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

    print "IBM iot raspberry client server start listening."
    while True:
        time.sleep(1)

except ibmiotf.ConnectionException as e:
    print e

