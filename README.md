# Happy Plants - by FPJA group
## Members

Francesca Cavallo

Patrick Mabin

Jesus E. Garcia

## Our IoT Plant monitoring solution
The product we have developed is a system based on the IoT containing a plant monitoring device, a server and a client application. The monitoring device is to be placed on a plant to automatically water it and gather information. This information is initially partially processed in the device to develop a *plant index* which is a percentage score of how well the plant is doing. The server gathers the latest plant index as well as other processed sensor data for the device. To save energy the device only pulishes and does not receive MQTT messages. The server is both an MQTT subscriber and publisher which simultaneously deals with the device and the client. It takes requests from the client and replies with the necessary information. 

## How to run
### IoTDevice
Our device requieres a _ESP8266_ module with i2c compatible sensors Si7021 and tsl2561 with _SCL_ connected to pin 5 and _SDA_ connected to pin 4. It also requires a PWM servo attached to pin 12 and a button attached to pin 15.

To program the device connect it through usb and run `sudo sh program.sh`. This will update the time to initialise the RTC clock in the device, load the device with `IoTDevice.py` and open a terminal to view output. This requires `ampy` and `screen` to be installed.

### Server
To run the server simply run `python server.py` in a device connected to the same wifi as the device. There will be terminal output to confirm connection and show incoming and outgoing messages.

### Client

To simulate the mobile application the final product would have as a client, command line tools have been developed. These use one terminal to query the server and another to view the replies. First run `source client_commands.sh` to setup the tools. Then runnning `monitor` in one screen runs a client to view the replies. Running commands of the type `query_<type>` sends requests to the server. For more details see `client_commands.sh`
