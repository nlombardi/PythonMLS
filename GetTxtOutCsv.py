import json
import pandas as pd

# define variables
fieldnames = ["Profile", "Name", "POS", "GP", "GS", "A", "GWA", "HmA", "RdA", "A/90min"]
fields = ["goals", "goalkeeping", "saves", "shots", "shutouts", "fouls"]
directory = "/Users/nlomb/Documents/Development/Python/MLS/txt/"
drct = "/Users/nlomb/Documents/Development/Python/MLS/csv/"

for year in range(1996, 2019):

	# initiate the dataframe to store the full data in:
	REG_Full = pd.DataFrame()

	# import assists file ofr year: year
	infile = open(directory + 'REG_' + str(year) + '_assists.txt')
	data = json.load(infile)
	infile.close()
	
	# convert to a data frame, sort values by name ascending, reset the index to 0
	REG_Assists = pd.DataFrame(data)
	REG_Assists.sort_values('Name', ascending=True, inplace=True)
	REG_Assists.reset_index(drop=True, inplace=True)
	
	for field in fields:
		
		# import other files to append to
		infile = open(directory + 'REG_' + str(year) + '_' + field + '.txt')
		data = json.load(infile)
		infile.close()
		
		# convert to a datafrme, sort values by name ascending, reset the index to 0
		REG_Field = pd.DataFrame(data)
		REG_Field.sort_values('Name', ascending=True, inplace=True)
		REG_Field.reset_index(drop=True, inplace=True)
		
		# initiate dataframe to store sliced data
		Column = pd.DataFrame()

		if len(REG_Assists['Name']) < len(REG_Field['Name']):
		
			print ('Assists Length: ' + len(REG_Assists['Name']), field + ' Length: ' + len(REG_Field['Name']))
		
			for a in REG_Field.loc[:, 'Name']:
			
				print (a)
				
				index_a = REG_Field['Name'].values.tolist().index(a)
				
				if REG_Assists.loc[index_a, 'Name'] == REG_Field.loc[index_a + 1, 'Name']:
					
					
					
				elif REG_Assists.loc[index_a, 'Name'] == REG_Field.loc[index_a + 1, 'Name']:
				
					REG_Assists[index_a, 'Name'].append(REG_Field.loc[index_a, 'Name'])
					
					print (REG_Assists.loc[index_a, 'Name'] + ' |  ' + REG_Field.loc[index_a, 'Name'])
					
				else:
				
					print ("Data is out of order and cannot be concatenated") 
				

		# loops through two dataframes and gets the column: Name, sorts the columns, and compares them
		for a, b in zip(REG_Assists.loc[:, 'Name'], REG_Field.loc[:, 'Name']):
			
			if a == b:
				
				# get the index of the value 'b' and assign to variable
				index_b = REG_Field['Name'].values.tolist().index(b)
				
				# append each row under column goals corresponding to the index_b
				# for each column name that is different than the column names found in REG_Assists
				
				for col in list(REG_Field.columns.values):
				
					# checks to see if the column name exists, if not adds it.
					if col not in fieldnames and col not in Column.columns.tolist():
						Column[col] = col
					
					# if column name exists, checks to see if the value exists in index_b
					# elif REG_Field.loc[index_b, col] == Column.loc[index_b, col]:
						# print ("Record already exists")
						
					Column.loc[index_b, col] = REG_Field.loc[index_b, col]
				
			else:
			
				for c in REG_Field.loc[:, 'Name']:
				
					if c == a:
						
						# get the index of the value 'a' and assign to variable
						index_c = REG_Field['Name'].values.tolist().index(c)
						
						for col in list(REG_Field.columns.values):
							if col not in fieldnames and col not in Column.columns.tolist():
								Column[col] = col
								Column.loc[index_c, col] = REG_Field.loc[index_c, col]
								
		# print (Column)
						
		# concatenate the column into the file REG_year
		REG_Full = pd.concat([Column], axis=1)
				
		# reset the column for the next file
		Column = pd.DataFrame()

	REG_Full.to_csv(drct + 'REG_' + str(year) + '_Full.csv', sep=',', encoding='utf-8')	
