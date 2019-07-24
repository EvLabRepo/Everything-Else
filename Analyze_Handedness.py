#This python script does the following
#	Read each csv file
#	Make sure the csv file is properly formatted
#	If not properly formatted, store mistake text
# 		else calculate L/R score
#	If the name does not already exist in the master csv file, then write
import os
import pdb
import csv
import pandas as pd
import re


#Helper functions below

#Get all csv names
def get_all_csvs(path2csvs):
	csvs = []
	for file in os.listdir(path2csvs):
		if file.endswith(".csv"):
			csvs.append(file)
	return csvs

def find_new_subjs(csvs):
	#If master_csv does not exist, all subjs are new.
	if "master_scores.csv" not in os.listdir():
		return csvs
	else:
		return csvs
		# new_subjs = []
		# #Read master_scores
		# df = pd.read_csv("master_scores.csv")
		# #Load subjects
		# subjects = df["Subject_ID"]
		# #Find the difference between csv column1 and csvs list
		# pass

def calculate_score(df):
	#Grab the relevant lines and cast to int
	try:
		scores = df.iloc[0].values.astype(int)
	except:
		pdb.set_trace()
	#Calculate scores according to similar http://zhanglab.wdfiles.com/local--files/survey/handedness.html
	alwaysLeft = 0
	sometimesLeft = 1
	noPreference = 2
	sometimesRight = 3
	alwaysRight = 4

	alwaysMultiplier = 2

	sumR =   sum(scores == alwaysRight)*alwaysMultiplier \
	       + sum(scores == sometimesRight) \
	       + sum(scores == noPreference)

	sumL =   sum(scores == alwaysLeft)*alwaysMultiplier \
	       + sum(scores == sometimesLeft) \
	       + sum(scores == noPreference)


	BasicMeasure1 = (sumR - sumL) / (sumR + sumL)
	BasicMeasure2 = sumR / 20

	score_struct = {'BasicMeasure1': BasicMeasure1, 'BasicMeasure2':BasicMeasure2}
	return score_struct
	

def write_scores(path2csvs,new_subs):
	#Go through each csv
	outDF = pd.DataFrame(columns=['csv_ID', 'sub_ID', '(sumR - sumL) / (sumR + sumL)','sumR / 20','notes'])
	for sub in new_subs:
		#Load subject csv as dataframe
		sub_path = os.path.join(path2csvs,sub)
		try:
			df = pd.read_csv(sub_path,header=None,error_bad_lines=False)
		except:
			outDF = outDF.append({'csv_ID': sub, 'sub_ID': sub_id, '(sumR - sumL) / (sumR + sumL)': 'NaN',\
									'sumR / 20':'NaN', 'notes':'Error reading csv'}, ignore_index=True)
		#Parse subject id
		result = re.search('results_(.*).csv', sub)
		sub_id = result.group(1)
		#Check formatting: length of responses
		if len(df.iloc[0]) != 10:
			outDF = outDF.append({'csv_ID': sub, 'sub_ID': sub_id, '(sumR - sumL) / (sumR + sumL)': 'NaN',\
									'sumR / 20':'NaN', 'notes':'CSV rows not 10'}, ignore_index=True)
			continue
		#Check that first row can even be loaded 
		try:
			scores = df.iloc[0].values.astype(int)
		except:
			outDF = outDF.append({'csv_ID': sub, 'sub_ID': sub_id, '(sumR - sumL) / (sumR + sumL)': 'NaN',\
								'sumR / 20':'NaN', 'notes':'Could not read first csv row'}, ignore_index=True)
			continue

		#Passed format test, so calculate score and write
		scores = calculate_score(df)
		outDF = outDF.append({'csv_ID': sub, 'sub_ID': sub_id, '(sumR - sumL) / (sumR + sumL)': scores['BasicMeasure1'],\
									'sumR / 20':scores['BasicMeasure2'], 'notes':''}, ignore_index=True)
	outDF.to_csv('master_scores.csv',index=False)

#Main function
if __name__=="__main__":
	#Path to where individual responses are
	path2csvs = './LangTask_Walid_Matt_Evlab_Full_2019/HandednessSinistrality/results'
	#Get all_csvs
	csvs = get_all_csvs(path2csvs)
	#Find which subjects are new subjects compared to the master csv
	#new_subs = find_new_subjs(csvs)
	#Caculate and write scores to master_scores.csv
	write_scores(path2csvs, csvs)



#Iterate through the csvs
