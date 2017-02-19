#client_commands.sh
#FPJA group
#Feb 2017
#
# Script to load to terminal aliases for commands that simulate a client 
# in our IoT plant monitoring solution. Actuall device would have a mobile
# version client. This command line tools where developed for illustration.
# The can be used by opening two terminals and runing
# 
# 	source client_commands.sh
# 
# Then in one of them open a monitor to view the replies from the server
# 
# 	monitor
# 
# Use the other terminal to send requests to the server by running any of the
# following:
#
#	query_index		
#	query_avg_day	
#	query_avg_week	
#	query_avg_<index/water/temp/light>	
#	query_bad	


alias query_index='mosquitto_pub -h 192.168.0.10 -d -t /esys/FPJA/server/rqst -m "{\"rqst\": \"index\"}"'
alias query_avg_day='mosquitto_pub -h 192.168.0.10 -d -t /esys/FPJA/server/rqst -m "{\"rqst\": \"avg\", \"type\": \"all\", \"length\": \"Daily\"}"'
alias query_avg_week='mosquitto_pub -h 192.168.0.10 -d -t /esys/FPJA/server/rqst -m "{\"rqst\": \"avg\", \"type\": \"all\", \"length\": \"Weekly\"}"'
alias query_avg_water='mosquitto_pub -h 192.168.0.10 -d -t /esys/FPJA/server/rqst -m "{\"rqst\": \"avg\", \"type\": \"light\", \"length\": \"Daily\"}"'
alias query_avg_temp='mosquitto_pub -h 192.168.0.10 -d -t /esys/FPJA/server/rqst -m "{\"rqst\": \"avg\", \"type\": \"temp\", \"length\": \"Daily\"}"'
alias query_avg_light='mosquitto_pub -h 192.168.0.10 -d -t /esys/FPJA/server/rqst -m "{\"rqst\": \"avg\", \"type\": \"light\", \"length\": \"Daily\"}"'
alias query_avg_index='mosquitto_pub -h 192.168.0.10 -d -t /esys/FPJA/server/rqst -m "{\"rqst\": \"avg\", \"type\": \"index\", \"length\": \"Daily\"}"'
alias query_bad='mosquitto_pub -h 192.168.0.10 -d -t /esys/FPJA/server/rqst -m "{\"rqst\": \"avg\", \"typ\": \"index\", \"length\": \"Daily\"}"'
alias monitor='mosquitto_sub -h 192.168.0.10 -t /esys/FPJA/client'
