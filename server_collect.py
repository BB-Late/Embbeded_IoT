import paho.mqtt.client as mqtt  
from heapq import *
import json 
import time

base_topic = "/esys/FPJA"
server_topic = base_topic + "/server"
client_topic = base_topic + "/client"
index_topic = server_topic + "/index"
rqst_topic = server_topic + "/rqst"
avg_topic = server_topic + "/avg"


def on_connect(client, userdata, flags, rc):
    m="Connected with client1_id  "+str(client)
    print(m)

def on_avg_message(client1, userdata, message):
    msg_content = message.payload.decode("utf-8")
    print("Avg received  "  , json.dumps(str(msg_content), indent = 2))
    heappush(msg_queue, msg_content)

def on_index_message(client1, userdata, message):
    msg_content = message.payload.decode("utf-8")
    print("Index received  "  , json.dumps(str(msg_content), indent = 2))
    global curr_index  
    curr_index = msg_content 
    print(curr_index)
    print(type(curr_index))

def on_rqst_message(client1, userdata, message):
    msg_content = message.payload.decode("utf-8")
    print("Request received  "  ,str(msg_content))
    curr_index = message.payload.decode("utf-8")
    heappush(rqst_queue, msg_content)
    interrupt = True
#    if collecting:
#        raise SystemExit()

def on_message(client1, userdata, message):
    print("ERR: Message from unrecognized topic:  ", message.topic, 
                " content: "  ,str(message.payload.decode("utf-8")))

def payload_to_str(payload):
    data = json.loads(payload)
    time = str_timestamp(data["timestamp"])
    entries = ["avg", "max", "min"]
    water = [str(data["water"][entry]) for entry in entries] 
    temp = [str(data["temp"][entry]) for entry in entries]
    light = [str(data["light"][entry]) for entry in entries]
    data = json.loads(curr_index)
    return " ".join([time] + water + temp + light + [str(data["index"])]) + '\n'

def pretty_print_timestamp(timestamp):
    return str(timestamp["Day"])+ "/" + str(timestamp["Month"]) + \
            " at " + str(timestamp["Hour"]) + ":" + str(timestamp["Min"])

def str_timestamp(timestamp):
    return " ".join([str(timestamp["Day"]),  str(timestamp["Month"]),
                     str(timestamp["Hour"]),  str(timestamp["Min"])])
    
def reply_index():
    answ = ""
    if curr_index == None:
        answ = "Waiting for first index"
    else:
        data = json.loads(curr_index)
        answ = "On " + pretty_print_timestamp(data["timestamp"])
        answ += "\nPlant has life index of: " + str(data["index"]) + "%"
        answ += "\n      was last wateres at: " + \
                 pretty_print_timestamp(data["last_watered"])
        answ += "\n      water tank at: " + \
                 str(data["water_level"]*10) + "%"
    return answ
    
def reply_avg(avg_type, avg_length):
    import server 
    import itertools 
    avg_types = ["water", "temp", "light", "index"]
    avg_lengths = ["Daily", "Weekly"]
    avg_units = {"water" : "% RH", "temp":"Celsius", "light": "Lumens", "index": "%"}
    if avg_type != "all":
        avg_types = [avg_type]
        avg_lenths = [avg_length]
    elif avg_type == "all" or avg_length == "all":
        if avg_type != "all":
            avg_types = [avg_type]
        if avg_length != "all":
            avg_lengths = [avg_length]

    elif not avg_type in avg_types or not avg_length in avg_lengts:
        return None
    answ = ""
    for avg_type, avg_length in list(itertools.product(avg_types, avg_lengths)):
        if avg_type == "index":
            avg = server.avg_index(server.file_data,
                                                    avg_type, avg_length)
            answ += "\n" + avg_length + " values for ~"+ avg_type + "~ are:"
            answ += "\n    Avg: " + str(avg) + avg_units[avg_type]
        else:
            avg, max_v, min_v = server.avg_max_min(server.file_data,
                                                    avg_type, avg_length)
            answ += "\n" + avg_length + " values for ~"+ avg_type + "~ are:"
            answ += "\n    Min: " + str(min_v) + avg_units[avg_type]
            answ += "\n    Avg: " + str(avg) + avg_units[avg_type]
            answ += "\n    Max: " + str(max_v) + avg_units[avg_type]
    return answ

msg_queue =[] 
rqst_queue =[] 
curr_index = None 
collecting = False 
interrupt = False 

broker_address="192.168.0.10"
#broker_address="127.0.0.1"
client1 = mqtt.Client("P1")    #create new instance
client1.on_connect= on_connect        #attach function to callback
client1.on_message= on_message        #attach function to callback

time.sleep(1)
#client1.connect(broker_address, port=1025)      #connect to broker
client1.connect(broker_address)      #connect to broker
client1.message_callback_add(avg_topic, on_avg_message)
client1.message_callback_add(rqst_topic, on_rqst_message)
client1.message_callback_add(index_topic, on_index_message)
client1.subscribe(server_topic + "/#", 2)
client1.publish(client_topic, "Client connected to server", 2)
client1.loop_start()    #start the loop

end = False
while not end:
    print "Looping"
    try:
        collecting = True
        with open('real_datalog.txt', 'a') as outputfile:
            while msg_queue:
                file_line = payload_to_str(msg_queue.pop())
                outputfile.write(file_line)
                if interrupt:
                    raise SystemExit

        time.sleep(5)
        collecting = False 
    except SystemExit:
        collecting = False 
        interrupt = False 
        print("Prioritizing requests")
    except KeyboardInterrupt:
        print("Ending data collection")
        end = True
    while rqst_queue:
        print("Processing request")
        rqst_data = rqst_queue.pop()
        rqst = json.loads(rqst_data)
        try :
            if "rqst" in rqst:
                if rqst["rqst"] == "index":
                    reply = reply_index()
                elif rqst["rqst"] == "avg":
                    if "type" in rqst and "length" in rqst: 
                        reply = reply_avg(rqst["type"], rqst["length"])
                        if reply == None:
                            raise ValueError()
                    else:
                        raise ValueError()
                else:
                    raise ValueError()
            else:
                raise ValueError()
            print("Publishing good answ: ", reply)
            client1.publish(client_topic, reply, 2)
        except ValueError:
            answ_wrong = "Received bad request: " + json.dumps(rqst_data) + \
                         """format must be: 
                                        {\"rqst\": index}
                                        or
                                        {\"rqst\": avg, 
                                        \"type\" :  <water/temp/light/index>, 
                                        \"length\" :  <Daily/Weekly>}"""
            print("Publishing bad answ: ", answ_wrong)
            client1.publish(client_topic, answ_wrong, 2)
                                
client1.disconnect()
client1.loop_stop()


