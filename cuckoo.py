import random
import hashlib

class CuckooFilter:
    def __init__(self, num_buckets, bucket_size, max_kicks):
        self.num_buckets = num_buckets
        self.bucket_size = bucket_size
        self.max_kicks = max_kicks
        self.buckets = [[] for _ in range(num_buckets)]
        self.num_items = 0

    def insert(self, item):
        if self.contains(item):
            return True

        if self.num_items >= self.num_buckets:
            return False

        index1 = self._get_index(item)
        index2 = (index1 ^ self._get_fingerprint(item)) % self.num_buckets

        for _ in range(self.max_kicks):
            if not self.buckets[index1]:
                self.buckets[index1].append(self._get_fingerprint(item))
                self.num_items += 1
                return True

            if not self.buckets[index2]:
                self.buckets[index2].append(self._get_fingerprint(item))
                self.num_items += 1
                return True

            eviction_index = random.choice([index1, index2])
            eviction_fingerprint = random.choice(self.buckets[eviction_index])
            self.buckets[eviction_index].remove(eviction_fingerprint)
            self.buckets[eviction_index].append(self._get_fingerprint(item))

            item = self._get_item(eviction_fingerprint)
            index1 = self._get_index(item)
            index2 = (index1 ^ self._get_fingerprint(item)) % self.num_buckets

        return False

    def contains(self, item):
        index1 = self._get_index(item)
        index2 = (index1 ^ self._get_fingerprint(item)) % self.num_buckets
        return self._get_fingerprint(item) in self.buckets[index1] or self._get_fingerprint(item) in self.buckets[index2]

    def _get_index(self, item):
        hash_value = hashlib.sha256(str(item).encode()).hexdigest()
        return int(hash_value, 16) % self.num_buckets

    def _get_fingerprint(self, item):
        hash_value = hashlib.sha256(str(item).encode()).hexdigest()
        return int(hash_value, 16) & ((1 << self.bucket_size) - 1)

    def _get_item(self, fingerprint):
        for bucket in self.buckets:
            for item in bucket:
                if self._get_fingerprint(item) == fingerprint:
                    return item

        return None

