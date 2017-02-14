import paho.mqtt.client as mqtt  
from heapq import *
import json 
import time

base_topic = "/esys/FPJA"
server_topic = base_topic + "/server"

def on_connect(client, userdata, flags, rc):
    m="Connected with client1_id  "+str(client)
    print(m)

def on_message(client1, userdata, message):
    print("message received  "  ,str(message.payload.decode("utf-8")))
    heappush(msg_queue, message.payload.decode("utf-8"))

def payload_to_str(payload):
    data = json.loads(payload)
    times = str(data["timestamp"])
    entries = ["min", "max", "avg"]
    water = [str(data["water"][entry]) for entry in entries] 
    temp = [str(data["temp"][entry]) for entry in entries]
    light = [str(data["light"][entry]) for entry in entries]
    return " ".join([str(times)] + water + temp + light) + '\n'

msg_queue =[] 

#broker_address="192.168.0.10"
broker_address="127.0.0.1"
client1 = mqtt.Client("P1")    #create new instance
client1.on_connect= on_connect        #attach function to callback
client1.on_message= on_message        #attach function to callback

time.sleep(1)
client1.connect(broker_address, port=1024)      #connect to broker
client1.loop_start()    #start the loop
client1.subscribe(server_topic, 2)

end = False
while not end:
    print "Looping"
    try:
        with open('real_datalog.txt', 'a') as outputfile:
            while msg_queue:
                file_line = payload_to_str(msg_queue.pop())
                outputfile.write(file_line)

        time.sleep(5)
    except KeyboardInterrupt:
            print("Ending data collection")
            end = True
        

time.sleep(5)
client1.disconnect()
client1.loop_stop()


