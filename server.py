#Python auxiliary code to run server side of application

columns = {"water": 4, "temp": 7, "light": 10, "index": 13}

def avg_max_min(data, column_name, period):
        column = columns[column_name]
	avg_col = column
        if column_name == "index":
            max_col = column
	    min_col = column
        else:    
            max_col = column +1
	    min_col = column +2

	if (period == "Daily"):		
                sm = data[0][avg_col]
		mx = data[0][max_col]
		mn = data[0][min_col]
		count = 0;
		for i in range(len(data)-1):
                        #Still in the same day:
			if (data[i+1][0] == data[i][0]):
				sm = sm + data[i][avg_col] 
				if data[i][max_col] > mx:	
					mx = data[i][max_col]
				if data[i][min_col] < mn:
					mn = data[i][min_col]
                        #New day
                        else: 
                            break
		return (sm/len(data), mx, mn)


	if (period == "Weekly"):		
		sm = data[0][avg_col]
		mx = data[0][max_col]
		mn = data[0][min_col]
		count = 0;
		for i in range(len(data)-1):
			while count < 7: 
				if data[i+1][0] == data[i][0]\
                                or data[i+1][0] == data[i][0]+1:
					sm = sm + data[i][avg_col]
					if data[i][max_col] > mx:
						mx = data[i][max_col]
					if data[i][min_col] < mn:
						mn = data[i][min_col]
					count = count +1
				if count == 7:
					break
		return (sm/len(data), mx, mn)

file_data = []
with open('real_datalog.txt') as inputfile:
    	for row in inputfile:
	    	file_data.append(row.strip().split(' '))

#data from file with format: 
# day month hours minutes water(avg,max,min), temp(3), water(3), light(3), index(1)
file_data = [map(float, i) for i in file_data]  
