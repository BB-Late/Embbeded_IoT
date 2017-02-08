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
 
#SI7021 tm=emmperature sensor Address and commands

SI7021_I2C_DEFULT_ADDR = 0x44

CMD_MEASURE_RELAVTIVE_HUMIDITY = 0xF5
CMD_MEASURE_TEMPERATURE = 0xF3

 #----------------------------------------------------------------------------------------------------------
    
# Not sure we need theses functions, they only contain one command from the revelant library.

def ReadLight(light): # Reading from light sensor
    light = L_sensor.read()
    
def ReadTemp(temp): # Reading from Temperature library
    temp = temp_sesnor.readTemp()
    
def ReadHumidity(humid): # Reading from Temperature library
    humid = temp_sensor.readRH()
    
#--------------------------------------------------------------------------------------------------------
    
def ServoMove():# Opens servo motor 
    servo.duty(130)
    time.sleep(0.5)
    servo.duty(30)

class device_status(object):
    
    def __init__(self):
        self.average_every = 4       
        self.average_count = 0       
 
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

    def sample():
	
	esp.sleep_type(SLEEP_NONE)
############  PATRICK  ####################
#Update all of this and water if necessary
	self.index = 0

	last_waterd = 0

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

############  END PATRICK  ####################

	last_sensed = time.localtime(time.time())
	report_basic()

	self.average_count += 1
	if self.average_count == self.average_every:
		report_full()
	esp.sleep_type(SLEEP_LIGHT)

    def report_basic():
	publish_full_data(self.last_sensed, self.index, self.water_level) 
	
    def report_full():
	publish_full_data(self.last_sensed, 
                        self.water_avg, self.water_min, self.water_max, 
                        self.temp_avg, self.temp_min, self.temp_max, 
                        self.light_avg, self.light_min, self.light_max, 
                        )
	


if __name__ == '__main__':
    
    i2c = I2C(Pin(5), Pin(4)) # Setup the i2c channel
    L_sensor = tsl2561.TSL2561(i2c) # Setup the light sesnor
    temp_sensor = si7021.Si7021() # Setupthe temperature and humidity Sensor 
    servo = machine.PWM(machine.PIN(12), freq = 50) # Setup for servo motor
    
    servo.duty(30) #Setting the inital posistion of the servo motor

    mike = device_status()
    
    sense_time_sec = 2 
    sense_time =  sense_time_sec*1000

    tim = machine.Timer(-1)
    tim.init(period=5000, mode=Timer.PERIODIC, callback=mike.sense())	
    
    print(sensor.read())

    #TODO: Implement deepsleep
#    # configure RTC.ALARM0 to be able to wake the device
#    rtc = machine.RTC()
#    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
#    
#    # check if the device woke from a deep sleep
#    if machine.reset_cause() == machine.DEEPSLEEP_RESET:
#        print('woke from a deep sleep')
#    
#    # set RTC.ALARM0 to fire after 10 seconds (waking the device)
#    rtc.alarm(rtc.ALARM0, 10000)
#    
#    # put the device to sleep
#    machine.deepsleep()
 


