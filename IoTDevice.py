import utime as time
import tsl2561 # Library for light sensor
import network
#import si7021   # need to get library from here https://gist.github.com/minyk/7c3070bc1c2766633b8ff1d4d51089cf
from machine import I2C, Pin
from umqtt.simple import MQTTClient

machine_name = machine.unique_id() 



base_topic = "/esys/FPJA/"
server_topic = base_topic + "/server/"
def publish(topic, data_json):
    client = MQTTClient(machine_name,"192.168.0.10")
    client.connect()
    #client.publish(topic,bytes(data,'utf-8'))
    client.publish(topic, json.dumps(data_json))
    
    
def networkConnection():
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    sta_if.active(True)
    sta_if.connect('EEERover','exhibition')

def publish_index(timestamp, index, last_watered, water_level):
    json_payload={  "timestamp": timestamp,
                    "index": index,
                    "last_watered": last_watered,
                    "water_level": water_level
                    }
    publish(server_topic, json_payload)

def publish_full_data(timestamp, 
                        water_avg, water_min, water_max, 
                        temp_avg, temp_min, temp_max, 
                        light_avg, light_min, ligh_max, 
                        ):
    json_payload={  "timestamp": timestamp,
                    "water": { 
                        "avg": water_avg,
                        "min": water_min,
                        "max": water_max
                        },
                    "temp": { 
                        "avg": temp_avg,
                        "min": temp_min,
                        "max": temp_max
                        },
                    "light": { 
                        "avg": light_avg,
                        "min": light_min,
                        "max": ligh_max
                        },
                    }
    publish(server_topic, json_payload)
 
#SI7021 temperature sensor Address and commands

SI7021_I2C_DEFULT_ADDR = 0x44

CMD_MEASURE_RELAVTIVE_HUMIDITY = 0xF5
CMD_MEASURE_TEMPERATURE = 0xF3

class Si7021(object):# Code copied from Si7021 library, may need to be changed
    def __init__(self, i2c_addr = SI7021_I2C_DEFAULT_ADDR):
        self.addr = i2c_addr
        self.cbuffer = bytearray(2)
        self.cbuffer[1] = 0x00
        self.i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)

    def write_command(self, command_byte):
        self.cbuffer[0] = command_byte
        self.i2c.writeto(self.addr, self.cbuffer)

    def readTemp(self):
        self.write_command(CMD_MEASURE_TEMPERATURE)
        sleep_ms(25)
        temp = self.i2c.readfrom(self.addr,3)
        temp2 = temp[0] << 8
        temp2 = temp2 | temp[1]
        return (175.72 * temp2 / 65536) - 46.85

    def readRH(self):
        self.write_command(CMD_MEASURE_RELATIVE_HUMIDITY)
        sleep_ms(25)
        rh = self.i2c.readfrom(self.addr, 3)
        rh2 = rh[0] << 8
        rh2 = rh2 | rh[1]
        return (125 * rh2 / 65536) - 6
    

 #----------------------------------------------------------------------------------------------------------
    
# Not sure we need theses functions, they only contain one command from the revelant library.

def ReadLight(light): # Reading from light sensor
    light = append(L_sensor.read())
    
def ReadTemp(temp): # Reading from Temperature library
    temp = append(temp_sensor.readTemp())
    
def ReadHumidity(humid): # Reading from Temperature library
    humid = append(temp_sensor.readRH())
    
#--------------------------------------------------------------------------------------------------------

def collectData(light, temp, water, data_time):#Data collection all at once 
    light = append(L_sensor.read())
    temp = append(temp_sensor.readTemp())
    water = append(temp_sensor.readRH())
    data_time = append(time.time())# records time of readings
    
    
def ServoMove(water_level):# Opens servo motor 
    servo.duty(130)
    time.sleep(0.5)
    servo.duty(30)
    

class device_status(object):
    
    def __init__(self):
	self.water_level = 0
	self.water_avg = 0
	self.water_min = 0
	self.water_max = 0
	
	self.temp_avg = 0
	self.temp_min = 0
	self.temp_max = 0
	
	self.light_avg = 0
	self.light_min = 0
	self.light_max = 0

############  PATRICK  ####################
#Update all of this and water if necessary
    def sample():
	
	self.index = 0

	last_waterd = 0

	self.water_level = 0

	self.water_avg = 0 #
	self.water_min = 0
	self.water_max = 0
	
	self.temp_avg = sum(temp)/float(len(temp)) # finds the mean of the temperature
	self.temp_min = min(temp)
	self.temp_max = max(temp)
	
	self.light_avg = sum(light)/float(len(light)) # finds the mean of the light readings 
	self.light_min = min(light)
	self.light_max = max(light)

############  END PATRICK  ####################

	last_sensed = time.localtime(time.time())

    def report_basic():
	publish_full_data(self.last_sensed, self.index, self.water_level) 
	
    def report_full():
	publish_full_data(self.last_sensed, 
                        self.water_avg, self.water_min, self.water_max, 
                        self.temp_avg, self.temp_min, self.temp_max, 
                        self.light_avg, self.light_min, self.light_max, 
                        )
	


if __name__ == '__main__':
    
    # configure RTC.ALARM0 to be able to wake the device
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    
    # check if the device woke from a deep sleep
    if machine.reset_cause() == machine.DEEPSLEEP_RESET:
        print('woke from a deep sleep')
    
    # set RTC.ALARM0 to fire after 10 seconds (waking the device)
    rtc.alarm(rtc.ALARM0, 10000)
    
    # put the device to sleep
    machine.deepsleep()
 
    i2c = I2C(Pin(5), Pin(4)) # Setup the i2c channel
    L_sensor = tsl2561.TSL2561(i2c) # Setup the light sesnor
    temp_sensor = si7021.Si7021() # Setupthe temperature and humidity Sensor 
    servo = machine.PWM(machine.PIN(12), freq = 50) # Setup for servo motor
    
    servo.duty(30) #Setting the inital posistion of the servo motor
    


