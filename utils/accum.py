import os
csv_src_dir = ""

# Create aggregated csv file.
with open(os.path.join(csv_src_dir, "accum.csv"), 'w') as fh:
	pass

files = os.listdir(csv_src_dir)

with open(os.path.join(csv_src_dir, "accum.csv"), "a") as acc_fh:
	for filename in files:
        if filename = "accum.csv":
                continue
        with open(os.path.join(csv_src_dir, filename), 'a') as fh:
            data = fh.read()
            acc_fh.write(data)
            acc_fh.write(["\n"])
	                
