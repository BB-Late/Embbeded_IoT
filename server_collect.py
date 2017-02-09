import paho.mqtt.client as mqtt  
from heapq import *
from json import *
import time

base_topic = "/esys/FPJA/"
server_topic = base_topic + "/server/"

def on_connect(client, userdata, flags, rc):
    m="Connected with client1_id  "+str(client)
    print(m)

def on_message(client1, userdata, message):
    print("message received  "  ,str(message.payload.decode("utf-8")))

def payload_to_str(payload):
    data = json.load(payload)
    times = data["timestamp"]
    water = [val for val in data["water"]]
    temp = [val for val in data["temp"]]
    light = [val for val in data["light"]]
    return " ".join(times + water + temp + light)

msg_queue =[] 

broker_address="192.168.0.10"
client1 = mqtt.Client("P1")    #create new instance
client1.on_connect= on_connect        #attach function to callback
client1.on_message= on_message        #attach function to callback
time.sleep(1)
client1.connect(broker_address)      #connect to broker
client1.loop_start()    #start the loop
client1.subscribe(server_topic)

end = False
while not end:
    try:
        with open('real_datalog.txt') as outputfile:
            while msg_queue:
                file_line = payload_to_str(msg_queue.pop().payload)
                outputfile.write(file_line)
    except KeyboardInterrupt:
            print("Ending data collection")
            end = True
        

time.sleep(5)
client1.disconnect()
client1.loop_stop()


