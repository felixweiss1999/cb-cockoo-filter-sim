from bloom import BloomFilter
from cuckoo import CuckooFilter
m = 1000 #bitarray length
k = 12 #number of hash functions

bf = BloomFilter(size=m, num_hash_functions=k)
d = CuckooFilter(num_buckets=500, bucket_size=4, fingerprint_len=10)
print(d.compute_filter_occupancy(), d.compute_false_positive_rate())
for i in range(10000, 10500):
    d.insert(str(i))
print(d.compute_filter_occupancy(), d.compute_false_positive_rate())
fpc = 0
for i in range(3000, 7000):
    if d.lookup(str(i)):
        fpc += 1
print(fpc)

cpc = 0
for i in range(10000, 10500):
    if d.lookup(str(i)):
        cpc += 1
print(cpc)


