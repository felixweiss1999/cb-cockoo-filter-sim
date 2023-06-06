from bloom import BloomFilter
from cuckoo import CuckooFilter, CBCuckooFilter
import numpy as np
import json
import threading


def measureFPR(num_buckets, fingerprint_size, target_occupancy):
    cf = CuckooFilter(num_buckets=num_buckets, bucket_size=4, fingerprint_len=fingerprint_size)
    cbcf = CBCuckooFilter(num_buckets=num_buckets, bucket_size=4, fingerprint_len=fingerprint_size)
    bloom = BloomFilter(size=num_buckets*4*fingerprint_size, num_hash_functions=round(0.69*num_buckets*4*fingerprint_size/(num_buckets*4*0.95)))
    print("Num hash functions for bloom:", round(0.69*num_buckets*4*fingerprint_size/(num_buckets*4*0.95)))
    for i in range(int(target_occupancy * num_buckets * 4)):
        cf.insert(str(i))
        cbcf.insert(str(i))
        bloom.insert(str(i))
    print(f"Cuckoo Filter: \n    Occupancy: {cf.compute_filter_occupancy()}\n    Expected FPR: {cf.compute_false_positive_rate()}")
    print(f"Configurable-Bucket Cuckoo Filter: \n    Occupancy: {cbcf.compute_filter_occupancy()}\n    Expected FPR: {cbcf.compute_false_positive_rate()}")
    cbcf.scrub()
    cbcf.scrub()
    cbcf.scrub()
    cbcf._test_verify_state()
    print(f"After Scrubbing: Expected FPR: {cbcf.compute_false_positive_rate()}")
    print(f"Bloom Filter: \n    Expected FPR: {bloom.compute_false_positive_rate()}")
    cf_fpr = 0
    cbcf_fpr = 0
    bloom_fpr = 0
    runs = 100
    lookups = 1000000
    for j in range(runs):
        cf_fp = 0
        cbcf_fp = 0
        bloom_fp = 0
        for i in range(int(target_occupancy * num_buckets * 4)+j * lookups, int(target_occupancy * num_buckets * 4) + j * lookups + lookups):
            if cf.lookup(str(i)):
                cf_fp += 1
            if cbcf.lookup(str(i)):
                cbcf_fp += 1
            if bloom.lookup(str(i)):
                bloom_fp += 1
        cf_fpr += cf_fp / lookups
        cbcf_fpr += cbcf_fp / lookups
        bloom_fpr += bloom_fp / lookups
    cf_fpr /= runs
    cbcf_fpr /= runs
    bloom_fpr /= runs
    print(f"Cuckoo Filter:\n    Actual FPR: {cf_fpr}")
    print(f"Configurable-Bucket Cuckoo Filter:\n    Actual FPR: {cbcf_fpr}")
    print(f"Bloom Filter:\n    Actual FPR: {bloom_fpr}")
    entity = {
        "parameters": {
            "num_buckets": num_buckets,
            "fingerprint_size": fingerprint_size,
            "target_occupancy": target_occupancy
        },
        "measurements": {
            "cf_fpr_e": cf.compute_false_positive_rate(),
            "cf_fpr": cf_fpr,
            "cbcf_fpr_e": cbcf.compute_false_positive_rate(),
            "cbcf_fpr": cbcf_fpr,
            "bloom_fpr_e": bloom.compute_false_positive_rate(),
            "bloom_fpr": bloom_fpr
        }
    }
    return entity

start = 0.3
end = 1.0
step = 0.05

def worker(start, end, step, fingerlength):
    for value in [start + i * step for i in range(int((end - start) / step) + 1)]:
        measurement = measureFPR(8192, fingerlength, value)
        filename = "measurements"+str(fingerlength) + ".txt"
        with open(filename, "a") as file:
            json.dump(measurement, file)
            file.write('\n')


thread1 = threading.Thread(target=worker, args=(start, end, step, 18))
thread2 = threading.Thread(target=worker, args=(start, end, step, 15))
thread3 = threading.Thread(target=worker, args=(start, end, step, 12))

thread1.start()
thread2.start()
thread3.start()
thread1.join()
thread2.join()
thread3.join()
