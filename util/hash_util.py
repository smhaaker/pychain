import hashlib
import json


def hash_string_256(string):
    return hashlib.sha256(string).hexdigest()


def hash_block(block):
    """ returns hash block

    Arguments: 
        :block: The Block That Will Be Hashed
    """
    hashable_block = block.__dict__.copy()
    # ordered dict
    hashable_block['transactions'] = [tx.to_ordered_dict()
                                      for tx in hashable_block['transactions']]
    return hash_string_256(json.dumps(hashable_block, sort_keys=True).encode())
    # return hash_string_256(json.dumps(block, sort_keys=True).encode())
    # return '-'.join([str(block[key]) for key in block])
    # use sort_keys to true to sort keys before hashing
