from bloom import BloomFilter
from cuckoo import CuckooFilter, CBCuckooFilter
m = 1000 #bitarray length
k = 12 #number of hash functions

bf = BloomFilter(size=m, num_hash_functions=k)
d = CBCuckooFilter(num_buckets=100, bucket_size=4, fingerprint_len=12)

print(d.compute_filter_occupancy(), d.compute_false_positive_rate())
d._test_verify_state()
for i in range(300):
    d.insert(str(i))
d._test_verify_state()
print(d.compute_filter_occupancy(), d.compute_false_positive_rate())
for i in range(100):
    for j in range(len(d.actual_elements[i])):
        if d.actual_elements[i][j] == '190':
            print("i", i)
for i in range(200):
    d.delete(str(i))
d._test_verify_state()
print(d.compute_filter_occupancy(), d.compute_false_positive_rate())
d.scrub()
d._test_verify_state()
print(d.compute_filter_occupancy(), d.compute_false_positive_rate())