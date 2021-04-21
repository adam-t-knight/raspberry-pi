from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import time as t
import json
import re

def readTemp(sensorName):
    if sensorName:
        dir = '/sys/bus/w1/devices/%s/w1_slave' % sensorName
        with open(dir,'r') as f:
            lines = f.readlines()
            f.close()

        if 'YES' in lines[0]:
            match = re.search('t=(\d+)$',lines[1])
            if match:
                temp = float( match.group(1) ) / 1000
                return temp

    return 'unknown'

sensor = '28-01205fac9d72'
temp = readTemp(sensor)
print('Temperature reading is', temp)

# Define ENDPOINT, CLIENT_ID, PATH_TO_CERT, PATH_TO_KEY, PATH_TO_ROOT, MESSAGE, TOPIC, and RANGE
ENDPOINT = "a20y97ene3px6o-ats.iot.us-east-2.amazonaws.com"
CLIENT_ID = "AdamClientID"
PATH_TO_CERT = "/home/pi/certs2/511f2aa63a-certificate.pem.crt"
PATH_TO_KEY = "/home/pi/certs2/511f2aa63a-private.pem.key"
PATH_TO_ROOT = "/home/pi/certs2/AmazonRootCA1.pem"
MESSAGE = temp
TOPIC = "aws-iot-app"

# Spin up resources
event_loop_group = io.EventLoopGroup(1)
host_resolver = io.DefaultHostResolver(event_loop_group)
client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=ENDPOINT,
            cert_filepath=PATH_TO_CERT,
            pri_key_filepath=PATH_TO_KEY,
            client_bootstrap=client_bootstrap,
            ca_filepath=PATH_TO_ROOT,
            client_id=CLIENT_ID,
            clean_session=False,
            keep_alive_secs=6
            )
print("Connecting to {} with client ID '{}'...".format(
        ENDPOINT, CLIENT_ID))
# Make the connect() call
connect_future = mqtt_connection.connect()
# Future.result() waits until a result is available
connect_future.result()
print("Connected!")
# Publish message to server desired number of times.
print('Begin Publish')
message = {"message" : MESSAGE}
mqtt_connection.publish(topic=TOPIC, payload=json.dumps(message), qos=mqtt.QoS.AT_LEAST_ONCE)
print("Published: '" + json.dumps(message) + "' to the topic: " + "'aws-iot-app'")
print('Publish End')
disconnect_future = mqtt_connection.disconnect()
disconnect_future.result()