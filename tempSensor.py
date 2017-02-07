import time
import tsl2561
import network


from machine import I2C, Pin

def readLight(light):
    light = sensor.read()
    
def networkConnection():
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    sta_if.active(True)
    sta_if.connect('EEERover','exhibition')
    
def MQTTConnect():
    from umqtt.simple import MQTTClient
    client = MQTTClient
    

if __name__ == '__main__':

    i2c = I2C(Pin(5), Pin(4))
    sensor = tsl2561.TSL2561(i2c)
    print(sensor.read())