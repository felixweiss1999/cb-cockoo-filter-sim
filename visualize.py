import json
import matplotlib.pyplot as plt

filename = "measurements12.txt"
entities = []

with open(filename, "r") as file:
    for line in file:
        entity = json.loads(line)
        entities.append(entity)

occupancies = []
cf_fpr_e = []
cf_fpr = []
cbcf_fpr_e = []
cbcf_fpr = []
bloom_fpr_e = []
bloom_fpr = []
for entity in entities:
    m = entity['measurements']
    cf_fpr_e.append(m['cf_fpr_e'])
    cf_fpr.append(m['cf_fpr'])
    cbcf_fpr_e.append(m['cbcf_fpr_e'])
    cbcf_fpr.append(m['cbcf_fpr'])
    bloom_fpr_e.append(m['bloom_fpr_e'])
    bloom_fpr.append(m['bloom_fpr'])

    p = entity['parameters']
    occupancies.append(p['target_occupancy'])

x = occupancies

# Plot each measurement as a line
plt.plot(x, cf_fpr_e, label='Expected Cuckoo')
plt.plot(x, cf_fpr, label='Cuckoo')
plt.plot(x, cbcf_fpr_e, label='Expected CB Cuckoo')
plt.plot(x, cbcf_fpr, label='CB Cuckoo')
plt.plot(x, bloom_fpr_e, label='Expected Bloom')
plt.plot(x, bloom_fpr, label='Bloom')

# Add labels and legend
plt.xlabel('X-axis')
plt.ylabel('Measurement Values')
plt.legend()

# Show the plot
plt.show()