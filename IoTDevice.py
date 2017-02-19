import utime
import machine 
import tsl2561  # Library for light sensor, copied to memory of device
import ujson    #  source: https://github.com/adafruit/micropython-adafruit-tsl2561
import network
from machine import I2C, Pin
import esp
import math
from umqtt.simple import MQTTClient

utc = (2017, 02, 16, 4, 11, 21, 18, 0)
machine.RTC().datetime(utc)


machine_name = machine.unique_id()
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('EEERover','exhibition')
client = MQTTClient(machine_name,"192.168.0.10")
client.connect()

base_topic = "/esys/FPJA"
server_topic = base_topic + "/server"
index_topic = server_topic + "/index"
avg_topic = server_topic + "/avg"
    
 
def publish(topic, data_json):
    client.publish(topic, ujson.dumps(data_json))
    

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


# Library for the Si7021 sensor for humidity and temperature
# Included as code and not imported for debugging and understanding
# Required small changes
#   Source: https://gist.github.com/minyk/7c3070bc1c2766633b8ff1d4d51089cf
class Si7021(object):
    SI7021_I2C_DEFAULT_ADDR = 0x40
    CMD_MEASURE_RELATIVE_HUMIDITY = 0xF5
    CMD_MEASURE_TEMPERATURE = 0xF3
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



class device_status(object):
    
    def __init__(self):
        print("Started device at: " , utime.localtime())
        self.pin_4 = Pin(4)
        self.pin_5 = Pin(5)

        #-1 selects software I2C implementation since no dedicated hardware
        self.i2c = I2C(-1, self.pin_5, self.pin_4) 
        self.light_sensor = tsl2561.TSL2561(self.i2c) 
        self.temp_sensor = Si7021(self.i2c)
        self.servo = machine.PWM(machine.Pin(12), freq = 50) 

        #Setting the inital posistion of the servo motor to water closed
        self.servo.duty(30)         
        self.average_every = 4       
        self.average_count = 0    
      
        #Variables to hold current readings
        self.light = 0
        self.temp = 0
        self.water = 0
        
        self.index = 0
        self.last_watered = 0  

        #Water tank starts empty, need user to refill
        self.water_level = 0

        # Flag for when the water needs to be topped up
        self.need_water = False         

        # Ideal Values for plant, used for plant index 
        self.ideal_light = 28 
        self.ideal_temp = 22
        self.ideal_water = 50
        
        # Plant index indicates health of plant as percentage
        self.water_index = 0
        self.temp_index = 0
        self.light_index = 0 
        self.total_index = 0 
        
        self.watering_time = 3 
    
        self.start_time = utime.time()
        self.last_sense_t = utime.time()
    def read_sensors(self): 
        self.light = self.light_sensor.read()
        self.temp = self.temp_sensor.readTemp()
        self.water = self.temp_sensor.readRH()
        
            
    def watering(self):
        # Check if the water needs to be toppped up
        if self.water_level == 0:
            self.need_water = True
        else:
            #Water since there is water available
            print("Watering")
            self.need_water = False
            self.open_water()
            self.water_level -= 1
            self.last_watered = utime.time()
    
    def open_water(self): 
        self.servo.duty(130)
        utime.sleep(2)
        self.servo.duty(30)

    #Callback from irq triggered by refill button
    def refill(self, irq):
        self.water_level = 10
        print("Refilled")

    # Humidity must be around an ideal value close to 50%
    # Values from 30% to 70% receive a score form 50%-100% as
    #   a function of their deviation from thei ideal
    # Extreme values < 30% and >70% can only achieve a 50% score
    def index_water(self): 
        if self.water <= 30: 
            self.water_index = (self.water/30)*50
        elif self.water <= 70:
            self.water_index = \
                    (math.fabs((self.water - self.ideal_water))/20)*50+50
        elif self.water >70:
            self.water_index = ((100-self.water)/30)*50
    
    # Temperature must be around an ideal value with small deviation
    # Index is a function of the deviation from the ideal value such that:
    #       index is 100% - 70% if temperature within 5% deviation
    #       index is 70% - 30% if temperature within 5-15% deviation
    #       index is 30% - 0% if temperature over 15% deviation
    def index_temp(self):
        value = (math.fabs(self.temp - self.ideal_temp))/self.ideal_temp
        if value <=0.05: 
            self.temp_index =((0.05-value)/0.05)*30 + 70
        elif value <= 0.15: 
            self.temp_index = ((0.15-value)/0.15)*40 + 30
        else: 
            self.temp_index = (1-value)*30
            
    def index_light(self):
        value = self.light/self.ideal_light
        if value >= 1:
            self.light_index = 100
        else:
            self.light_index = value*100
    
    # The overal index is the average of indexes
    def index_total(self): 
        self.index_water()
        self.index_temp()
        self.index_light()
        self.index = self.light_index/3 + self.temp_index/3 + self.water_index/3
    
    def pretty_print_sample(self):
        return "Sample: {} Lux {} C {} %RH \n\tPlant is {}% well".format(
                        self.light, self.temp, self.water, self.index)

    def pretty_print_avg(self):
        return "\tReporting rolling averages: {} Lux {} C {} %RH".format(
                            self.light_avg, self.temp_avg, self.water_avg)

    #Sample is called periodically to:
        # Wake up
        # Read sensors
        # Calculate plant index
        # Report plant index
        # Update rolling averages, min, max
        # Report rolling values every average_every samples
        # Set sleep
    def sample(self, tim):	
    
        esp.sleep_type(esp.SLEEP_NONE)
	
        self.read_sensors()

        if self.average_count == 0:
            self.water_min = self.water
            self.water_max = self.water
            
            self.temp_min = self.temp
            self.temp_max = self.temp
            
            self.light_min = self.light
            self.light_max = self.light
            
            self.start_time = utime.time()
            self.last_sense_t = utime.time()
        else:
            self.curr_sense_t = utime.time()
            self.averaging_time = self.curr_sense_t - self.last_sense_t
            self.total_time = self.curr_sense_t - self.start_time
            self.last_sense_t = self.curr_sense_t
            
            
            #Change to rolling average

	    self.cur_avg_fraction = (self.total_time - self.averaging_time)\
                                            /self.total_time
	    self.new_avg_fraction = (self.averaging_time)\
                                            /self.total_time
	    
            self.water_avg = self.water_avg*self.cur_avg_fraction \
                            + self.water*self.new_avg_fraction
            self.water_min = min((self.water_min, self.water))
            self.water_max = max((self.water_max, self.water))
            
            self.temp_avg = self.temp_avg*self.cur_avg_fraction \
                            + self.temp*self.new_avg_fraction
            self.temp_min = min((self.temp_min, self.temp))
            self.temp_max = max((self.temp_max, self.temp))
            
            self.light_avg = self.light_avg*self.cur_avg_fraction \
                            + self.light*self.new_avg_fraction
            self.light_min = min((self.light_min, self.light))
            self.light_max = max((self.light_max, self.light))

            self.index_total()
            self.report_basic()

            print(self.pretty_print_sample())
        
        self.average_count += 1
        if self.average_count == self.average_every:
        	self.report_full()
                print(self.pretty_print_avg())
                self.average_count = 0
                
	
        self.watering_time -= 1 
        if self.watering_time == 0:
            self.watering()
            self.watering_time = 6
        
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


# For demonstration purposes the device was set up from
# a terminal connection by calling:
#       import IoTDevice:
#       IoTDevice.run()
# This allowed to start an interrupt sample taking trough
# Keyboard signals and provided screen output.
#
# On the final prototype this would be set up in the boot.py
# file of the ESP8266 which runs on setup
def run():  
    # Mike is the nickname of our current prototype
    mike = device_status()

    # Sensing time would be substantially higher for working device
    # Kept low for demonstration
    sense_time_sec = 5 
    sense_time =  sense_time_sec*1000
    utime.sleep(sense_time_sec)

    # Set periodic sampling
    tim = machine.Timer(-1)
    tim.init(period=sense_time, mode=tim.PERIODIC, callback=mike.sample)	
    
    # Set irq for pressing of refill button
    # Button found to bounce, triggering multiple irq
    # but since refilling multiple times in a fraction of
    # second keeps the same result (water is full), button
    # was not debounced to save unnecessary computation
    p0 = Pin(15, Pin.IN)
    p0.irq(trigger=Pin.IRQ_RISING, handler=mike.refill)
    
    # Loop until there is a keyboard interrupt
    end = False
    while not end:
        try:
            utime.sleep(5)
        except KeyboardInterrupt:
            #Disable periodic sampling
    	    tim.init(period=sense_time, mode=tim.ONE_SHOT, 
					callback=lambda t : 0) 
            print("Ending data collection")
            end = True
    
