from flask import Flask,redirect
from flask import render_template
from flask import request
import os, json
import time
import ibmiotf.application

client = None
error = ""

def myCommandCallback(cmd):
    print "----- Receive command -----"
    print cmd.event
    print cmd.data


# vcap for testing 
"""
vcap = {
        "iotf-service": [{
            "name": "iot-python",
            "label": "iotf-service",
            "plan": "iotf-service-free",
            "credentials": {
                "iotCredentialsIdentifier": "a2g6k39sl6r5",
                "mqtt_host": "yd3lzz.messaging.internetofthings.ibmcloud.com",
                "mqtt_u_port": 1883,
                "mqtt_s_port": 8883,
                "base_uri": "https://yd3lzz.internetofthings.ibmcloud.com:443/api/v0001",
                "http_host": "yd3lzz.internetofthings.ibmcloud.com",
                "org": "yd3lzz",
                "apiKey": "a-yd3lzz-5pukcgmf52",
                "apiToken": "hBk1wcnjqkPzy?HHFt"
            }
        }]  
}

deviceId = "b827eb94758d"
options = {
    "org": vcap["iotf-service"][0]["credentials"]["org"],
    "id": vcap["iotf-service"][0]["credentials"]["iotCredentialsIdentifier"],
    "auth-method": "apikey",
    "auth-key": vcap["iotf-service"][0]["credentials"]["apiKey"],
    "auth-token": vcap["iotf-service"][0]["credentials"]["apiToken"]
}
options["deviceId"] = options["id"]
options["id"] = "aaa" + options["id"]
client = ibmiotf.application.Client(options)
client.connect()

client.deviceEventCallback = myCommandCallback
client.subscribeToDeviceEvents()

"""
try:
    vcap = json.loads(os.getenv("VCAP_SERVICES"))
    deviceId = os.getenv("DEVICE_ID")
    options = {
        "org": vcap["iotf-service"][0]["credentials"]["org"],
        "id": vcap["iotf-service"][0]["credentials"]["iotCredentialsIdentifier"],
        "auth-method": "apikey",
        "auth-key": vcap["iotf-service"][0]["credentials"]["apiKey"],
        "auth-token": vcap["iotf-service"][0]["credentials"]["apiToken"]
    }
    client = ibmiotf.application.Client(options)
    client.connect()

    client.deviceEventCallback = myCommandCallback
    client.subscribeToDeviceEvents(event="input")

except ibmiotf.ConnectionException as e:
    print e
    error = str(e)
except Exception as e:
    print e
    error = str(e)

app = Flask(__name__)

if os.getenv("VCAP_APP_PORT"):
    port = int(os.getenv("VCAP_APP_PORT"))
else:
    port = 8080

@app.route('/')
def hello():
    entries = []
    return render_template('index2.html', entries=entries)

@app.route('/takePicture', methods=['POST'])
def take_picture():
    myData = {}
    client.publishEvent("raspberrypi", deviceId, "take picture", "json", myData)
    return redirect("/", code=302)

if __name__ == '__main__':
    app.config['DEBUG'] = True
    print "starting server"
    app.run(host='0.0.0.0', port=port)
