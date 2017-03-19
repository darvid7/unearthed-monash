import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import Imputer
import time
from datetime import datetime

start = time.time()
TIME_LOOK_BACK = 1

def myDateTime(string, format="%Y-%m-%d %H:%M"):
	# please give this format "Y-m-d h:m"
	return datetime.strptime(string, format)

def myDateTimeDiff(datetime2, datetime1):
	# this gives diff in minutes for datetime2 - datetime1
	d1_ts = time.mktime(datetime1.timetuple())
	d2_ts = time.mktime(datetime2.timetuple())
	return int((d2_ts - d1_ts) / 60)

def getIndexOfDateTime(datetime):
	# this gives index of datetime relative to FIRSTDAY
	return myDateTimeDiff(datetime, FIRSTDAY)

FIRSTDAY = myDateTime("2015-01-01 00:00")

IS_NORMAL = 1
IS_BAD = -1
IS_IRRELEVANT = 2

# an array to keep track of the status of dates
datetimeStatus = [IS_NORMAL]*1100000

# we will assume that the 15 minutes before downtimes are bad
with open("Cadia HPGR 2 Years.csv", "r") as downTimes:
	allLines = downTimes.readlines()
	for line in allLines[1:]:
		splitLine = line.split(",")
		startDate = splitLine[4]
		endDate = splitLine[5]

		startDateTime = myDateTime(startDate[:-7])
		endDateTime = myDateTime(endDate[:-7])

		# all the bad date times only if it is unplanned
		if splitLine[10] == "Unplanned" and splitLine[11] in ["Operational", "Mechanical"]:
			for i in range(getIndexOfDateTime(startDateTime)-TIME_LOOK_BACK, getIndexOfDateTime(startDateTime)):
				datetimeStatus[i] = IS_BAD
		# all the irrelevant date times
		for i in range(getIndexOfDateTime(startDateTime), getIndexOfDateTime(endDateTime)+1):
			datetimeStatus[i] = IS_IRRELEVANT


# extract dataset
print("Preparing Data")
with open("20150101_20150201_3212SI005A.PV.csv", "r") as dataSet:
	allLines = dataSet.readlines()
	headers = allLines[0].split(",")
	content = allLines[1:-1]

	# list of dates that were used in data
	relevantDates = []
	# preprocess data
	relevantFeatures = []
	relevantResults = []

	i = 0
	for line in content:
		splitLine = line.split(",")

		# note current date
		thisDate = splitLine[0]

		thisRowData = []
		if datetimeStatus[i] < 2: # if relevant
			relevantDates.append(thisDate)
			relevantResults.append(datetimeStatus[i])
			for j in range(1,len(splitLine)):
				value = splitLine[j]
				try:
					thisRowData.append(float(value))
				except:
					thisRowData.append(np.nan)
			relevantFeatures.append(thisRowData)
		i+=1

	# count how many are bad to compute contamination
	lastDateTime = myDateTime(relevantDates[-1].replace(":00 PM", ""), "%d/%m/%Y %H:%M")
	countBad = 0
	for i in range(getIndexOfDateTime(lastDateTime)+1):
		if datetimeStatus[i] == -1:
			countBad += 1

	# use imputer for NaN values
	print("Imputing NaN values")
	imp = Imputer(missing_values='NaN', strategy='mean', axis=0)
	imp.fit(relevantFeatures)

	with open("relevantResults.txt", "w") as f:
		for i in relevantResults:
			f.write(str(i)+"\n")

	relevantFeatures = imp.transform(relevantFeatures)

	nSamples, nFeatures = relevantFeatures.shape

	# get train and test data
	percTrain = 0.8
	trainData = relevantFeatures[:int(percTrain*nSamples)]
	testData = relevantFeatures[int(percTrain*nSamples):]

	# create classifier
	print("Training Isolation Forest")
	rng = np.random.RandomState(42)

	contamination = countBad/nSamples
	# print(contamination)
	clf = IsolationForest(max_samples=len(trainData),
						  random_state=rng,
						  contamination=contamination,
						  max_features=nFeatures)
	clf.fit(trainData)

	print("Predicting")
	y_pred_train = clf.predict(trainData)
	y_pred_test = clf.predict(testData)

	print("Writing")
	totalCorrect = 0
	totalCorrectWhenBad = 1
	totalBad = 1
	with open("trainOutput.txt", "w") as trainOut:
		for i in range(len(y_pred_train)):
			trainOut.write(relevantDates[i] + ", " + str(y_pred_train[i]) + "\n")

			if y_pred_train[i] == relevantResults[i]:
				totalCorrect += 1
			if relevantResults[i] == IS_BAD:
				totalBad += 1
				if y_pred_train[i] == IS_BAD:
					totalCorrectWhenBad += 1
	print("Training Accuracy: {}%".format(totalCorrect/len(y_pred_train)*100))
	print("Training Accuracy when bad: {}%".format(totalCorrectWhenBad/totalBad*100))

	print()

	totalCorrect = 0
	totalCorrectWhenBad = 1
	totalBad = 1
	with open("testOutput.txt", "w") as testOutput:
		for i in range(len(y_pred_test)):
			testOutput.write(relevantDates[i+len(y_pred_train)] +", " + str(y_pred_test[i]) + "\n")

			if y_pred_test[i] == relevantResults[i+len(y_pred_train)]:
				totalCorrect += 1
			if relevantResults[i+len(y_pred_train)] == IS_BAD:
				totalBad += 1
				if y_pred_train[i] == IS_BAD:
					totalCorrectWhenBad += 1
	print("Testing Accuracy: {}%".format(totalCorrect/len(y_pred_test)*100))
	print("Testing Accuracy when bad: {}%".format(totalCorrectWhenBad/totalBad*100))

print()

print("Computed in {} seconds".format(time.time() - start))