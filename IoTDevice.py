import time
import tsl2561
import network
import si7021   # need to get library from here https://gist.github.com/minyk/7c3070bc1c2766633b8ff1d4d51089cf


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
    
 #----------------------------------------------------------------------------------------------------------
    
# Not sure we need theses functions, they only contain one command from the revelant library.

def ReadLight(light): # Reading from light sensor
    light = L_sensor.read()
    
def ReadTemp(temp): # Reading from Temperature library
    temp = temp_sesnor.readTemp()
    
def ReadHumidity(humid) # Reading from Temperature library
    humid = temp_sensor.readRH()
    
#--------------------------------------------------------------------------------------------------------
    
def ServoMove():# Opens servo motor 
    servo.duty(115)
    time.sleep(0.5)
    servo.duty(44)
    
def networkConnection():
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    sta_if.active(True)
    sta_if.connect('EEERover','exhibition')

if __name__ == '__main__':
    
    i2c = I2C(Pin(5), Pin(4)) # Setup the i2c channel
    L_sensor = tsl2561.TSL2561(i2c) # Setup the light sesnor
    temp_sensor = si7021.Si7021() # Setupthe temperature and humidity Sensor 
    servo = machine.PWM(machine.PIN(12), freq = 50) # Setup for servo motor
    
    print(sensor.read())
