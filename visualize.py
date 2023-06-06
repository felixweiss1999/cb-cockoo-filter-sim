import json
import matplotlib.pyplot as plt

filename = "measurements.txt"
entities = []

with open(filename, "r") as file:
    for line in file:
        entity = json.loads(line)
        entities.append(entity)

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


x = range(len(cf_fpr_e))

# Plot each measurement as a line
plt.plot(x, cf_fpr_e, label='Measurement 1')
plt.plot(x, cf_fpr, label='Measurement 2')
# plt.plot(x, measurement3_values, label='Measurement 3')
# plt.plot(x, measurement4_values, label='Measurement 4')
# plt.plot(x, measurement5_values, label='Measurement 5')
# plt.plot(x, measurement6_values, label='Measurement 6')

# Add labels and legend
plt.xlabel('X-axis')
plt.ylabel('Measurement Values')
plt.legend()

# Show the plot
plt.show()