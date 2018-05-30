import hashlib
import json


def hash_string_256(string):
    return hashlib.sha256(string).hexdigest()


def hash_block(block):
    """ returns hash block
    
    Arguments: 
        :block: The Block That Will Be Hashed
    """
    return hash_string_256(json.dumps(block, sort_keys=True).encode())
#    return '-'.join([str(block[key]) for key in block])
    # use sort_keys to true to sort keys before hashing
