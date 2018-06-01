from hash_util import hash_string_256, hash_block


class Verification:
    def valid_proof(self, transactions, last_hash, proof):
        """ Checks if new hash is valid

        Arguments: 
            :transactions:
            :last_hash:
            :proof: proof number / nonce
        """
        guess = (str([tx.to_ordered_dict for tx in transactions]) + str(last_hash) + str(proof)).encode() # concat a string
        guess_hash = hash_string_256(guess) # guessing if our guess is same as hash
        print(guess_hash)
        return guess_hash[0:2] == '00' # checking the leading zeros, if it is really a hash difficulty change
        # just add zeros to increase difficulty 

    def verify_chain(self, blockchain):
        """Verifies blockchain validity"""
        for (index, block) in enumerate(blockchain):
            if index == 0:
                continue
            if block.previous_hash != hash_block(blockchain[index - 1]):
                return False
            if not self.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print('proof of work invalid')
                return False
        return True

    # verifying transactions.
    def verify_transaction(self, transaction, get_balance):
        sender_balance = get_balance()
        if sender_balance >= transaction.amount:
            return True
        else: 
            return False

        # can also write as return sender_balance => transaction['amount]
        # since it just returns true or false. 


    def verify_transactions(self, open_transactions, get_balance):
        return all([self.verify_transaction(tx, get_balance) for tx in open_transactions])

        # the above is a list comprehension of whats below
        # using all, checks if all transactions are true. Any would check if at least one is true
        # is_valid = True
        # for tx in open_transactions:
        #     if verify_transaction(tx):
        #         is_valid = True
        #     else:
        #         is_valid = False
        #     return is_valid


