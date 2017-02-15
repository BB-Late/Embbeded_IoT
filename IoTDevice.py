import utime
#import time 
import machine 

utc = (2017, 02, 15, 3, 17, 40, 03, 0)
machine.RTC().datetime(utc)

import tsl2561 # Library for light sensor
import ujson 
import network
#import si7021   # need to get library from here https://gist.github.com/minyk/7c3070bc1c2766633b8ff1d4d51089cf
from machine import I2C, Pin
import esp
import math
from umqtt.simple import MQTTClient

machine_name = machine.unique_id() 



base_topic = "/esys/FPJA"
server_topic = base_topic + "/server"
index_topic = server_topic + "/index"
avg_topic = server_topic + "/avg"
 
def publish(topic, data_json):
    client = MQTTClient(machine_name,"192.168.0.10")
    client.connect()
    #client.publish(topic,bytes(data,'utf-8'))
    client.publish(topic, ujson.dumps(data_json))
    
def networkConnection():
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect('EEERover','exhibition')

def publish_index(timestamp, index, last_watered, water_level):
    json_payload={  "timestamp": timestamp,
                    "index": index,
                    "last_watered": last_watered,
                    "water_level": water_level
                    }
    publish(index_topic, json_payload)

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
    publish(avg_topic, json_payload)
 
#SI7021 temperature sensor Address and commands



class Si7021(object):# Code copied from Si7021 library, may need to be changed
    SI7021_I2C_DEFAULT_ADDR = 0x40
    CMD_MEASURE_RELATIVE_HUMIDITY = 0xF5
    CMD_MEASURE_TEMPERATURE = 0xF3
#    def __init__(self, i2c_in, i2c_addr = Si7021.SI7021_I2C_DEFAULT_ADDR):
    def __init__(self, i2c_in):
        self.addr = Si7021.SI7021_I2C_DEFAULT_ADDR
        self.cbuffer = bytearray(2)
        self.cbuffer[1] = 0x00
        self.i2c = i2c_in

    def write_command(self, command_byte):
        self.cbuffer[0] = command_byte
        self.i2c.writeto(self.addr, self.cbuffer)

    def readTemp(self):
        self.write_command(Si7021.CMD_MEASURE_TEMPERATURE)
        utime.sleep_ms(25)
        temp = self.i2c.readfrom(self.addr,3)
        temp2 = temp[0] << 8 #Shifts the bits by 8 over to the right
        temp2 = temp2 | temp[1] # Shift least significant byte to the back
        return (175.72 * temp2 / 65536) - 46.85 # calculation from data sheet

    def readRH(self):
        self.write_command(Si7021.CMD_MEASURE_RELATIVE_HUMIDITY)
        utime.sleep_ms(25)
        rh = self.i2c.readfrom(self.addr, 3)
        rh2 = rh[0] << 8 # shift bits by 8 over to the right
        rh2 = rh2 | rh[1] # Shift least significant byte to the back
        return (125 * rh2 / 65536) - 6 # Calculation from data sheet
    

 #----------------------------------------------------------------------------------------------------------
    
# Not sure we need theses functions, they only contain one command from the revelant library.

def ReadLight(light): # Reading from light sensor
    light = append(L_sensor.read())
    
def ReadTemp(temp): # Reading from Temperature library
    temp = append(temp_sensor.readTemp())
    
def ReadHumidity(humid): # Reading from Temperature library
    humid = append(temp_sensor.readRH())
    
#--------------------------------------------------------------------------------------------------------


    
    

class device_status(object):
    
    def __init__(self):
        print("Started device at: " , utime.localtime())
        self.pin_4 = Pin(4)
        self.pin_5 = Pin(5)

        #-1 selects software I2C implementation since no dedicated hardware
        self.i2c = I2C(-1, self.pin_5, self.pin_4) # Setup the i2c channel

        self.L_sensor = tsl2561.TSL2561(self.i2c) # Setup the light sesnor

        # Setupthe temperature and humidity Sensor 
        self.temp_sensor = Si7021(self.i2c)
        self.servo = machine.PWM(machine.Pin(12), freq = 50) # Setup for servo motor
        
        self.servo.duty(30) #Setting the inital posistion of the servo motor
        
        self.average_every = 4       
        self.average_count = 0    
           
        self.start_time = utime.time() # The starting time of data collection
        self.last_sense_t = utime.time(); # the ti0me before the last sample
        
        self.light = 0
        self.temp = 0
        self.water = 0
        
        self.index = 0
        self.last_watered = 0  

        self.water_level = 10 # Full water level will be 10, needs changing at zero
        self.need_water = False # Flag for when the water needs to be topped up
        #self.min_water_level = 10 # Water level that needs to be crossed before it is watered
        
        self.collectData()
        
        self.water_avg = self.water
        self.water_min = self.water
        self.water_max = self.water
        
        self.temp_avg = self.temp
        self.temp_min = self.temp
        self.temp_max = self.temp
        
        self.light_avg = self.light
        self.light_min = self.light
        self.light_max = self.light

        # Ideal Values for plant 
        self.ideal_light = 15
        self.ideal_temp = 22
        self.ideal_water = 50
        
        # plant score
        self.water_score = 0
        self.temp_score = 0
        self.light_score = 0 
        self.total_score = 0 
        
        self.watering_time = 6
    
    def collectData(self):#Data collection all at once 
        self.light = self.L_sensor.read()
        self.temp = self.temp_sensor.readTemp()
        self.water = self.temp_sensor.readRH()
        
    def MaxValue(self, old_max, new_value):
        if new_value > old_max:
            return new_value
        else:
            return old_max
    
    def MinValue(self, old_min, new_value):
        if new_value < old_min:
            return new_value
        else:
            return old_min
            
    def watering(self):
        if self.water_level == 0:# Check if the water needs to be toppped up
            self.need_water = True
        else:
            self.need_water = False
            self.ServoMove()
            self.water_level -= 1
            self.last_watered = utime.time()

    def ServoMove(self):# Opens servo motor 
        self.servo.duty(130)
        utime.sleep(2)
        self.servo.duty(30)
    def score_water(self):
        if self.water <= 30:
            self.water_score = (self.water/30)*50
        elif self.water <= 70:
            self.water_score = (math.fabs((self.water - self.ideal_water))/20)*50+50
        elif self.water >70:
            self.water_score = ((100-self.water)/30)*50
    
    def score_temp(self):
        value = (math.fabs(self.temp - self.ideal_temp))/self.ideal_temp
        if value <=0.05:
            self.temp_score =((0.05-value)/0.05)*30 + 70
        elif value <= 0.15:
            self.temp_score = ((0.15-value)/0.15)*40 + 30
        else: 
            self.temp_score = (1-value)*30
            
    def score_light(self):
        value = (math.fabs(self.temp - self.ideal_temp))/self.ideal_temp
        if value <=0.05:
            self.light_score =((0.05-value)/0.05)*30 + 70
        elif value <= 0.15:
            self.light_score = ((0.15-value)/0.15)*40 + 30
        else: 
            self.light_score = (1-value)*30
            
    def score_total(self):
        self.score_water()
        self.score_temp()
        self.score_light()
        self.index = self.light_score/3 + self.temp_score/3 + self.water_score/3
    
    def print_results(self):
        print('Light reading {} lux' .format(self.light))
        print('Temperature reading {} C' .format(self.temp))
        print('Humidity reading {} %' .format(self.water))
    
    def sample(self, tim):	
    
        esp.sleep_type(esp.SLEEP_NONE)

	
        if self.average_count == 0:
            self.start_time = utime.time()

        self.curr_sense_t = utime.time()
        self.averaging_time = self.curr_sense_t - self.last_sense_t
        self.total_time = self.curr_sense_t - self.start_time
        self.last_sense_t = self.curr_sense_t
        self.report_basic()
       
        
        self.collectData()
        
        #Change to rolling average

	self.cur_avg_fraction = (self.total_time - self.averaging_time)\
                                        /self.total_time
	self.new_avg_fraction = (self.averaging_time)\
                                        /self.total_time
	
        self.water_avg = self.water_avg*self.cur_avg_fraction \
                        + self.water*self.new_avg_fraction
        self.water_min = self.MinValue(self.water_min, self.water)
        self.water_max = self.MaxValue(self.water_max, self.water)
        
        self.temp_avg = self.temp_avg*self.cur_avg_fraction \
                        + self.temp*self.new_avg_fraction
        self.temp_min = self.MinValue(self.temp_min, self.temp)
        self.temp_max = self.MaxValue(self.temp_max, self.temp)
        
        self.light_avg = self.light_avg*self.cur_avg_fraction \
                        + self.light*self.new_avg_fraction
        self.light_min = self.MinValue(self.light_min, self.light)
        self.light_max = self.MaxValue(self.light_max, self.light)

        self.score_total()
        
        self.average_count += 1
        if self.average_count == self.average_every:
        	self.report_full()
                self.average_count = 0
	
        self.watering_time -= 1
        if self.watering_time == 0:
            self.watering()
            self.watering = 6
        
        esp.sleep_type(esp.SLEEP_LIGHT)
	

    def report_basic(self):
        publish_index(  self.t_to_timestamp(self.curr_sense_t), 
                        self.index, 
                        self.t_to_timestamp(self.last_watered), 
                        self.water_level) 
	
    def report_full(self):
	publish_full_data(
                        self.t_to_timestamp(self.curr_sense_t), 
                        self.water_avg, self.water_min, self.water_max, 
                        self.temp_avg, self.temp_min, self.temp_max, 
                        self.light_avg, self.light_min, self.light_max, 
                        )
    @staticmethod
    def t_to_timestamp(t_from_e):
        t = utime.localtime(t_from_e) 
        return {"Month": t[2], "Day": t[1], "Hour": (t[3]), "Min" : t[4]} 

    def pretty_print_sampe(self):
        return "Sample: {} Lux {} C {} %RH {} \n\tPlant is {}% well".format(
                        self.light, self.temp, self.water, sellf.index)

    
    def pretty_print_avg(self):
        return "Rolling averages: "


#if __name__ == '__main__':
def run():   
    print(utime.localtime())
    mike = device_status()

    sense_time_sec = 5 
    sense_time =  sense_time_sec*1000

    utime.sleep(sense_time_sec)
    tim = machine.Timer(-1)
    tim.init(period=sense_time, mode=tim.PERIODIC, callback=mike.sample)	
    end = False
    while not end:
        print("Looping")
        try:
            utime.sleep(5)
        except KeyboardInterrupt:
    	    tim.init(period=sense_time, mode=tim.ONE_SHOT, 
					callback=lambda t : 0) 
            print("Ending data collection")
            end = True
    

