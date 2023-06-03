from bloom import BloomFilter
from cuckoo import CuckooFilter
m = 1000 #bitarray length
k = 12 #number of hash functions

bf = BloomFilter(size=m, num_hash_functions=k)
d = CuckooFilter(num_buckets=5, bucket_size=4, fingerprint_len=13)
print(d.compute_filter_occupancy(), d.compute_false_positive_rate())
d.insert("hi")
print(d.compute_filter_occupancy(), d.compute_false_positive_rate())


