import random, mmh3
from bitarray import bitarray

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

    def insert(self, __item : str) -> bool:
        """
        Inserts byte-like object into the filter.

        Returns True if insert successful, otherwise False.
        """
        fingerprint = self._get_fingerprint(item=__item, len=self.fingerprint_len)
        index1 = mmh3.hash(key=__item, seed=1) % self.num_buckets
        index2 = (index1 ^ mmh3.hash(key=str(fingerprint), seed=2))  % self.num_buckets

        if len(self.buckets[index1]) < self.bucket_size:
            self.buckets[index1].append(fingerprint)
            self.num_items += 1
            return True

        if len(self.buckets[index2]) < self.bucket_size:
            self.buckets[index2].append(fingerprint)
            self.num_items += 1
            return True
        
        #need to enter evict procedure
        eviction_index = random.choice([index1, index2])
        for _ in range(self.max_kicks):
            if len(self.buckets[eviction_index]) < self.bucket_size:
                self.buckets[eviction_index].append(fingerprint)
                self.num_items += 1
                return True
            eviction_fingerprint = random.choice(self.buckets[eviction_index])
            self.buckets[eviction_index].remove(eviction_fingerprint)
            self.buckets[eviction_index].append(fingerprint)

            fingerprint = eviction_fingerprint #in next iter, fingerprint holds to be inserted fingerprint
            eviction_index = (eviction_index ^ mmh3.hash(key=str(fingerprint), seed=2)) % self.num_buckets#compute alternate bucket

        return False

    def lookup(self, __item : str) -> bool:
        """
        Always returns True if element was inserted.
        
        Most likely returns False if element was not inserted.
        
        May return True even if element was not inserted.
        """
        fingerprint = self._get_fingerprint(item=__item, len=self.fingerprint_len)
        index1 = mmh3.hash(key=__item, seed=1) % self.num_buckets
        index2 = (index1 ^ mmh3.hash(key=str(fingerprint), seed=2)) % self.num_buckets #might need to do another modulo
        return fingerprint in self.buckets[index1] or fingerprint in self.buckets[index2]

    def delete(self, __item : str):
        """
        Delete element of filter.

        Raises ValueError if element is not found.
        """
        fingerprint = self._get_fingerprint(item=__item, len=self.fingerprint_len)
        index1 = mmh3.hash(key=__item, seed=1) % self.num_buckets
        if fingerprint in self.buckets[index1]:
            self.buckets[index1].remove(fingerprint)
            return
        index2 = (index1 ^ mmh3.hash(key=str(fingerprint), seed=2)) % self.num_buckets
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
    
    def _get_fingerprint(self, item, len):
        return mmh3.hash(key=item) % (2**len)

class CBCuckooFilter(CuckooFilter):
    def __init__(self, num_buckets : int, bucket_size : int, fingerprint_len : int, max_kicks = 10):
        """
        Initializes a Configurable-Bucket Cuckoo Filter. This is a Cuckoo Filter which adjusts
        fingerprint length stored in the buckets based on filter occupancy. Achieves lower false 
        positive rate compared to ordinary CuckooFilter.

        Args:
            num_buckets: int > 0
            bucket_size: int > 0
            fingerprint_len: int > 0
            max_kicks: int > 0 : max number of retry iterations when inserting
        
        Raises ValueError if constraints not met.
        """
        super().__init__(num_buckets, bucket_size, fingerprint_len, max_kicks)
        self.sbits = bitarray(num_buckets)
        self.sbits.setall(1) #all empty!
        self.long_fingerprint_len = int(self.fingerprint_len + self.fingerprint_len/3)
        self.actual_elements = [[] for _ in range(num_buckets)]

    def insert(self, __item : str) -> bool:
        """
        Inserts byte-like object into the filter.

        Returns True if insert successful, otherwise False.
        """
        short_fingerprint = self._get_fingerprint(item=__item, len=self.fingerprint_len)
        long_fingerprint = self._get_fingerprint(item=__item, len=self.long_fingerprint_len)
        index1 = mmh3.hash(key=__item, seed=1) % self.num_buckets
        index2 = (index1 ^ mmh3.hash(key=str(short_fingerprint), seed=2))  % self.num_buckets
        if len(self.buckets[index1]) < len(self.buckets[index2]):
            insertindex = index1
        else:
            insertindex = index2

        if len(self.buckets[insertindex]) < self.bucket_size:
            if len(self.buckets[insertindex]) == self.bucket_size - 1:
                # special case: transforms long fingerprints into short ones.
                for i in range(len(self.buckets[insertindex])):
                    self.buckets[insertindex][i] = self._get_fingerprint(item=self.actual_elements[insertindex][i], len=self.fingerprint_len)
                self.buckets[insertindex].append(short_fingerprint)
                self.sbits[insertindex] = 0
            else:
                self.buckets[insertindex].append(long_fingerprint)
            self.actual_elements[insertindex].append(__item)
            self.num_items += 1
            return True

        
        
        #need to enter evict procedure
        eviction_index = random.choice([index1, index2])
        for _ in range(self.max_kicks):
            if len(self.buckets[eviction_index]) < self.bucket_size:
                if len(self.buckets[eviction_index]) == self.bucket_size - 1:
                    # special case: transforms long fingerprints into short ones.
                    for i in range(len(self.buckets[eviction_index])):
                        self.buckets[eviction_index][i] = self._get_fingerprint(item=self.actual_elements[eviction_index][i], len=self.fingerprint_len)
                    self.buckets[eviction_index].append(short_fingerprint)
                    self.sbits[eviction_index] = 0
                else:
                    self.buckets[eviction_index].append(self._get_fingerprint(item=__item, len=self.long_fingerprint_len)) #get this long one on the fly
                self.actual_elements[eviction_index].append(__item)
                self.num_items += 1
                return True
            eviction_fingerprint = self.buckets[eviction_index].pop()
            eviction_item = self.actual_elements[eviction_index].pop()
            self.buckets[eviction_index].append(short_fingerprint)
            self.actual_elements[eviction_index].append(__item)

            short_fingerprint = eviction_fingerprint # in next iter, short_fingerprint holds to be inserted short_fingerprint
            __item = eviction_item
            eviction_index = (eviction_index ^ mmh3.hash(key=str(short_fingerprint), seed=2)) % self.num_buckets # compute alternate bucket

        return False

    def lookup(self, __item : str) -> bool:
        """
        Always returns True if element was inserted.
        
        Most likely returns False if element was not inserted.
        
        May return True even if element was not inserted.
        """
        short_fingerprint = self._get_fingerprint(item=__item, len=self.fingerprint_len)
        long_fingerprint = self._get_fingerprint(item=__item, len=self.long_fingerprint_len)
        index1 = mmh3.hash(key=__item, seed=1) % self.num_buckets
        index2 = (index1 ^ mmh3.hash(key=str(short_fingerprint), seed=2)) % self.num_buckets
        if self.sbits[index1]:
            if long_fingerprint in self.buckets[index1]:
                return True
        else:
            if short_fingerprint in self.buckets[index1]:
                return True
        if self.sbits[index2]:
            if long_fingerprint in self.buckets[index2]:
                return True
        else:
            if short_fingerprint in self.buckets[index2]:
                return True
        return False

    def delete(self, __item : str):
        """
        Delete element of filter.

        Raises ValueError if element is not found.
        """
        pass

    def _test_verify_state(self):
        for i in range(self.num_buckets):
            #check length consistency
            assert len(self.buckets[i]) == len(self.actual_elements[i])
            #check sbits consistency
            if self.sbits[i]:
                assert len(self.buckets[i]) < self.bucket_size
                for j in range(len(self.buckets[i])):
                    assert self.buckets[i][j] == self._get_fingerprint(item=self.actual_elements[i][j], len=self.long_fingerprint_len)
            else:
                assert len(self.buckets[i]) == self.bucket_size
                for j in range(len(self.buckets[i])):
                    assert self.buckets[i][j] == self._get_fingerprint(item=self.actual_elements[i][j], len=self.fingerprint_len)
            
            
                