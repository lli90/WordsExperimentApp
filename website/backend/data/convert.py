import json

def removeFrontParts(line):
    parts = line.split(",")
    return ",".join(parts[2:])

data = None
with open("collisions125_trustwords.csv") as f:
    data = f.readlines()

# Removes header
data = data[1:]

# Strips all values
data = list(map(str.strip, data))
data = list(map(removeFrontParts, data))

output = {}
output["pairs"] = []

for i in range(0, len(data), 2):
    output["pairs"].append([data[i], data[i + 1]])


print(json.dumps(output))