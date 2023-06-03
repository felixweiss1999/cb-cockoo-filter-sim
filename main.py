from bloom import BloomFilter

m = 1000 #bitarray length
k = 12 #number of hash functions

bf = BloomFilter(size=m, num_hash_functions=k)

print(bf.lookup("HI"))
bf.insert("HI")
print(bf[0])

