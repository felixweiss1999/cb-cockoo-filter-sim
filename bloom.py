from bitarray import bitarray
import mmh3

class BloomFilter:
    def __init__(self, size : int, num_hash_functions: int):
        self.size = size
        self.bitarray = bitarray(size)
        self.bitarray.setall(0)
        self.num_hash_functions = num_hash_functions

    def insert(self, element : str) -> None:
        for i in range(self.num_hash_functions):
            self.bitarray[mmh3.hash(key=element, seed=i) % self.size] = 1

    def lookup(self, element : str) -> bool:
        for i in range(self.num_hash_functions):
            if self.bitarray[mmh3.hash(key=element, seed=i) % self.size] == 0:
                return False
        return True
    
    def __getitem__(self, index):
        return self.bitarray[index]