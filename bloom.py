from bitarray import bitarray
import mmh3

class BloomFilter:
    def __init__(self, size : int, num_hash_functions: int):
        """
        Initializes a Bloom Filter. Individual bits in bitarray
        accessible through [] operator.
        
        Args:
            size: int > 0
            num_hash_functions: int > 0
        
        Raises ValueError if conditions not met.
        """
        if size < 1 or num_hash_functions < 1:
            raise ValueError()
        self.size = size
        self.bitarray = bitarray(size)
        self.bitarray.setall(0)
        self.num_hash_functions = num_hash_functions
        self.num_items = 0

    def insert(self, __item : str) -> None:
        """
        Inserts argument into bitarray.
        """
        for i in range(self.num_hash_functions):
            self.bitarray[mmh3.hash(key=__item, seed=i) % self.size] = 1
        self.num_items += 1

    def lookup(self, __item : str) -> bool:
        """
        Checks if element was inserted. If element was
        inserted, returns True. If it was not inserted, 
        most likely returns False.
        """
        for i in range(self.num_hash_functions):
            if self.bitarray[mmh3.hash(key=__item, seed=i) % self.size] == 0:
                return False
        return True
    
    def compute_false_positive_rate(self) -> float:
        """
        Returns the false positive rate based on:

        (1-(1-1/m)**(k*n))**k where

        n: number of (individual) inserted elements

        k: number of hash functions used

        m: length of bitarray
        """
        return (1-(1-1/self.size)**(self.num_items * self.num_hash_functions))**self.num_hash_functions

    def __getitem__(self, index):
        return self.bitarray[index]