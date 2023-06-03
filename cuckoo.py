import random
import mmh3

class CuckooFilter:
    def __init__(self, num_buckets : int, bucket_size : int, fingerprint_len : int, max_kicks = 10):
        """
        Initializes a Cuckoo Filter

        Args:
            num_buckets: int > 0
            bucket_size: int > 0
            fingerprint_len: int > 0
            max_kicks: int > 0 : max number of retry iterations when inserting
        
        Raises ValueError if constraints not met.
        """
        if num_buckets < 1 or bucket_size < 1 or fingerprint_len < 1 or max_kicks < 1:
            raise ValueError()
        self.num_buckets = num_buckets
        self.bucket_size = bucket_size
        self.max_kicks = max_kicks
        self.fingerprint_len = fingerprint_len
        self.buckets = [[] for _ in range(num_buckets)]
        self.num_items = 0

    def insert(self, __item : str):
        if self.lookup(__item):
            return True

        if self.num_items >= self.num_buckets:
            return False

        index1 = self._get_index(__item)
        index2 = (index1 ^ self._get_fingerprint(__item)) % self.num_buckets

        for _ in range(self.max_kicks):
            if not self.buckets[index1]:
                self.buckets[index1].append(self._get_fingerprint(__item))
                self.num_items += 1
                return True

            if not self.buckets[index2]:
                self.buckets[index2].append(self._get_fingerprint(__item))
                self.num_items += 1
                return True

            eviction_index = random.choice([index1, index2])
            eviction_fingerprint = random.choice(self.buckets[eviction_index])
            self.buckets[eviction_index].remove(eviction_fingerprint)
            self.buckets[eviction_index].append(self._get_fingerprint(__item))

            __item = self._get_item(eviction_fingerprint)
            index1 = self._get_index(__item)
            index2 = (index1 ^ self._get_fingerprint(__item)) % self.num_buckets

        return False

    def lookup(self, __item : str):
        """
        Always returns True if element was inserted.
        
        Most likely returns False if element was not inserted.
        
        May return True even if element was not inserted.
        """
        fingerprint = self._get_fingerprint(item=__item)
        index1 = mmh3.hash(key=__item, seed=1) % self.num_buckets
        index2 = (index1 ^ (mmh3.hash(key=str(fingerprint), seed=2) % self.num_buckets)) #might need to do another modulo
        return fingerprint in self.buckets[index1] or fingerprint in self.buckets[index2]

    def delete(self, __item : str):
        """
        Delete element of filter.

        Raises ValueError if element is not found.
        """
        fingerprint = self._get_fingerprint(item=__item)
        index1 = mmh3.hash(key=__item, seed=1) % self.num_buckets
        if fingerprint in self.buckets[index1]:
            self.buckets[index1].remove(fingerprint)
            return
        index2 = (index1 ^ (mmh3.hash(key=str(fingerprint), seed=2) % self.num_buckets))
        if fingerprint in self.buckets[index2]:
            self.buckets[index2].remove(fingerprint)
            return 
        raise ValueError()

    def compute_false_positive_rate(self) -> float:
        """
        Returns the false positive rate based on:

        8 * filter_occupancy / 2**fingerprint_len
        """
        return 8 *self.compute_filter_occupancy() / 2**self.fingerprint_len
    
    def compute_filter_occupancy(self) -> float:
        """
        Returns the filter occupancy:  

        elements_stored / (num_buckets * bucket_size)
        """
        return self.num_items / (self.num_buckets * self.bucket_size)
    
    def _get_fingerprint(self, item):
        return mmh3.hash(key=item) % (2**self.fingerprint_len)

    def _get_item(self, fingerprint):
        for bucket in self.buckets:
            for item in bucket:
                if self._get_fingerprint(item) == fingerprint:
                    return item

        return None
