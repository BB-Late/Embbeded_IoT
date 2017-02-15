#Python code to run server side of application

############## functions ##################

columns = {"water": 4, "temp": 7, "light": 10, "index": 13}

#function that returns the average, max, min
def avg_max_min(data, column_name, period):
        column = columns[column_name]
	avg_col = column
	max_col = column +1
	min_col = column +2
#	print len(data)
#	print range(len(data))
	if (period == "Daily"):		#daily values
		sm = data[0][avg_col]
		mx = data[0][max_col]
		mn = data[0][min_col]
		count = 0;
		for i in range(len(data)-1):
			if (data[i+1][0] == data[i][0]): #if we are still in the same day
				sm = sm + data[i][avg_col] 
				if data[i][max_col] > mx:	
					mx = data[i][max_col]
				if data[i][min_col] < mn:
					mn = data[i][min_col]
			if (data[i+1][0] != data[i][0]): #if they day has changed break the loop and return
				break
		return (sm/len(data), mx, mn)


	if (period == "Weekly"):		#weekly values
		sm = data[0][avg_col]
		mx = data[0][max_col]
		mn = data[0][min_col]
		count = 0;
		for i in range(len(data)-1):
			while count < 7: 
				if data[i+1][0] == data[i][0] or data[i+1][0] == data[i][0]+1:
					sm = sm + data[i][avg_col]
					if data[i][max_col] > mx:
						mx = data[i][max_col]
					if data[i][min_col] < mn:
						mn = data[i][min_col]
					count = count +1
				if count == 7:
					break
		return (sm/len(data), mx, mn)

### only for plant index ###
def avg_index(data, column_name, period):
        column = columns[column_name]
	avg_col = column

	if (period == "Daily"):		#daily values
		sm = data[0][avg_col]
		count = 0;
		for i in range(len(data)-1):
			if (data[i+1][0] == data[i][0]): #if we are still in the same day
				sm = sm + data[i][avg_col] 
			if (data[i+1][0] != data[i][0]): #if they day has changed break the loop and return
				break
		return sm/len(data)


	if (period == "Weekly"):		#weekly values
		sm = data[0][avg_col]
		count = 0;
		for i in range(len(data)-1):
			while count < 7: 
				if data[i+1][0] == data[i][0] or data[i+1][0] == data[i][0]+1:
					sm = sm + data[i][avg_col]
					count = count +1
				if count == 7:
					break
		return sm/len(data)


######################### main ############################

#def __main__():


#upload data file
file_data = []
#with open('datalog.txt') as inputfile:
with open('real_datalog.txt') as inputfile:
    	for row in inputfile:
	    	file_data.append(row.strip().split(' '))

#convert into float
file_data = [map(float, i) for i in file_data]  #data: day month hours minutes water(avg,max,min), temp(3), water(3), light(3), index(1)
print file_data

#calculate values for water
#(water_avg_daily, water_max_daily, water_min_daily) = avg_max_min(file_data, 4, 1)
#(water_avg_weekly, water_max_weekly, water_min_weekly) = avg_max_min(file_data, 4, 2)
#
##temperature
#(temperature_avg_daily, temperature_max_daily, temperature_min_daily) = avg_max_min(file_data, 7, 1)
#(temperature_avg_weekly, temperature_max_weekly, temperature_min_weekly) = avg_max_min(file_data, 7, 2)
#
##light
#(light_avg_daily, light_max_daily, light_min_daily) = avg_max_min(file_data, 10, 1)
#(light_avg_weekly, light_max_weekly, light_min_weekly) = avg_max_min(file_data, 10, 2)
#
##index
#(index_avg_daily) = avg_index(file_data, 13, 1)
#(index_avg_weekly) = avg_index(file_data, 13, 2)
#
#calculate values for water
(water_avg_daily, water_max_daily, water_min_daily) = avg_max_min(file_data, "water", "Daily")
(water_avg_weekly, water_max_weekly, water_min_weekly) = avg_max_min(file_data, "water", "Weekly")

#temperature
(temperature_avg_daily, temperature_max_daily, temperature_min_daily) = avg_max_min(file_data, "temp", "Daily")
(temperature_avg_weekly, temperature_max_weekly, temperature_min_weekly) = avg_max_min(file_data, "temp", "Weekly")

#light
(light_avg_daily, light_max_daily, light_min_daily) = avg_max_min(file_data, "light", "Daily")
(light_avg_weekly, light_max_weekly, light_min_weekly) = avg_max_min(file_data, "light", "Weekly")

#index
(index_avg_daily) = avg_index(file_data, "index", "Daily")
(index_avg_weekly) = avg_index(file_data, "index", "Weekly")

