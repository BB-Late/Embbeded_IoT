import time
import tsl2561
import network


from machine import I2C, Pin
from umqtt.simple import MQTTClient

machine_name = machine.unique_id() 
base_topic = "/esys/FPJA/"
request_topic = base_topic + "/request/"

def publish(topic, data_json):
    client = MQTTClient(machine_name,"192.168.0.10")
    client.connect()
    #client.publish(topic,bytes(data,'utf-8'))
    client.publish(topic, json.dumps(data_json))

def readLight(light):
    light = sensor.read()
    
def networkConnection():
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    sta_if.active(True)
    sta_if.connect('EEERover','exhibition')

if __name__ == '__main__':
    
    i2c = I2C(Pin(5), Pin(4))
    sensor = tsl2561.TSL2561(i2c)
    print(sensor.read())
