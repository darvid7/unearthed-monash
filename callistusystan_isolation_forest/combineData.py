import os

OUTPUT = "combinedData.csv"

with open(OUTPUT, "w") as outputFile:
	first = True
	for filename in os.listdir("."):
		if filename.endswith(".csv") and filename != OUTPUT and filename.startswith("201"):
			print(filename)
			with open(filename, "r") as dataSet:
				allLines = dataSet.readlines()

				header = allLines[0]
				content = allLines[1:-1]

				if first:
					outputFile.write(header)
					first = False
				for line in content:
					outputFile.write(line)


