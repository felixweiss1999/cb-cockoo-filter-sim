import json

def read_measurements_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

        for line in lines:
            entry = json.loads(line)
            measurements = entry['measurements']

            # Extract the measurement values
            cf_fpr_e = measurements['cf_fpr_e']
            cf_fpr = measurements['cf_fpr']
            cbcf_fpr_e = measurements['cbcf_fpr_e']
            cbcf_fpr = measurements['cbcf_fpr']
            bloom_fpr_e = measurements['bloom_fpr_e']
            bloom_fpr = measurements['bloom_fpr']

            # Print the measurements separated by a space
            print(cf_fpr_e, cf_fpr, cbcf_fpr_e, cbcf_fpr, bloom_fpr_e, bloom_fpr)


# Usage example
file_path = 'measurements18.txt'  # Replace with the path to your file
read_measurements_from_file(file_path)