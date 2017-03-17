import os
csv_src_dir = "/Users/David/Desktop/unearthed-2017/unearthed-monash/unearthed-monash/Data/PI"

# Create aggregated csv file.
with open(os.path.join(csv_src_dir, "accum.csv"), 'w') as fh:
	pass

files = os.listdir(csv_src_dir)

count = 1
with open(os.path.join(csv_src_dir, "accum.csv"), "a") as acc_fh:
	for filename in files:
		if filename == "accum.csv":
			continue
		if not filename.endswith('.csv'):
			continue
		with open(os.path.join(csv_src_dir, filename), 'r') as fh:
			data = fh.read()
			data = ','.join([str(count), data])
			acc_fh.write(data)
			acc_fh.write("\n")
			count += 1
	                
