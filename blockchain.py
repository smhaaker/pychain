import functools
import hashlib
from collections import OrderedDict
import json 
import pickle #stores in binary and serializes it if wanted
import requests


# internal imports
from util.hash_util import hash_block, hash_string_256
from util.verification import Verification
from block import Block
from transaction import Transaction
from wallet import Wallet
#from verification import Verification
#from hash_util import hash_string_256, hash_block

MINING_REWARD = 10 # global constant 

print(__name__)

class Blockchain:
    def __init__(self, public_key, node_id):
        # genesis block
        genesis_block = Block(0, '', [], 100, 0)

        # empty list
        self.chain = [genesis_block] #private
        self.__open_transactions = [] #private
        self.public_key = public_key
        self.__peer_nodes = set()
        self.node_id = node_id # remove if not testinsg locally
        self.load_data()

    @property
    def chain(self):
        return self.__chain[:]    


    @chain.setter
    def chain(self,val):
        self.__chain = val




    # def get_chain(self):
    #     return self.__chain[:]


    def get_open_transactions(self):
        return self.__open_transactions[:]


    def load_data(self):
        """Load data"""
        try:
            with open('blockchain-{}.txt'.format(self.node_id), mode='r')as f:
                file_content = f.readlines()
                blockchain = json.loads(file_content[0][:-1]) #deserializes the string with range selector
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']]
                    # converted_tx = [OrderedDict(
                    #         [('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])]) for tx in block['transactions']] 
                    updated_block = Block(block['index'], block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                    # updated_block = {
                    #     'previous_hash': block['previous_hash'],
                    #     'index': block['index'],
                    #     'proof': block['proof'],
                    #     'transactions': [OrderedDict(
                    #         [('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])]) for tx in block['transactions']] 
                    # }
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain
                # to remove linebreak
                open_transactions = json.loads(file_content[1][:-1])
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount'])
                    # updated_transaction = OrderedDict(
                    #         [('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])]) 
                    updated_transactions.append(updated_transaction)
                self.__open_transactions = updated_transactions
                # loading nodes
                peer_nodes = json.loads(file_content[2])
                self.__peer_nodes = set(peer_nodes)
        except (IOError, IndexError):
            print('exception handler')
        finally:
            print('cleanup!')



    def save_data(self):
        """Saves data to file"""
        try:
            with open('blockchain-{}.txt'.format(self.node_id), mode='w')as f:
                saveable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash, [tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp) for block_el in self.__chain]]
                f.write(json.dumps(saveable_chain))
                f.write('\n')
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
                f.write(json.dumps(saveable_tx))
                f.write('\n')
                f.write(json.dumps(list(self.__peer_nodes)))
        except IOError:
            print('save failed')


    def proof_of_work(self):
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1    
        return proof


    def get_balance(self, sender=None):
        if sender == None:
            if self.public_key == None:
                return None
            participant = self.public_key
        else: 
            participant = sender
        tx_sender = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in self.__chain]
        # need to get open transactions sent using List Comprehension
        open_tx_sender = [tx.amount for tx in self.__open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)
        amount_sent = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
        # above is simpler reduce of below video #94
        # amount_sent = 0
        # for tx in tx_sender:
        #     if len(tx) > 0:
        #         amount_sent += tx[0]
        tx_recipient = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in self.__chain]
        amount_received = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)
        return amount_received - amount_sent


    # Get last blockchain value function
    def get_last_blockchain_value(self):
        """ Returns last blockchain value 
        
        Arguments: none
        """
        if len(self.__chain) < 1:
            return None # checking lenght of list
        return self.__chain[-1]


    # value function
    def add_transaction(self, recipient, sender, signature, amount=1.0, is_receiving=False):
        """ Adds a transaction to the chain 
        
        Arguments:
            :sender: sender of transaction (default owner)
            :recipent: recipent of transaction
            :amount: amount of transaction (default 1.0)
        """
        # transaction = {
        #     'sender': sender, 
        #     'recipient': recipient, 
        #     'amount': amount} # dictionary key value pair sender is key

        # check if we have wallet or not, If not we cant add transaction
        if self.public_key == None:
            return False
        # using a ordered dictionary instead
        # our key value pair becomes tuples instead
        transaction = Transaction(sender, recipient, signature, amount)
        # transaction = OrderedDict([('sender', sender), ('recipient', recipient), ('amount', amount)])
        if Verification.verify_transaction(transaction, self.get_balance): # if verify transaction successds then do following
            self.__open_transactions.append(transaction) # storing above transactions 
            self.save_data()
            if not is_receiving:
                for node in self.__peer_nodes:
                    url = 'http://{}/broadcast-transaction'.format(node)
                    try:
                        response = requests.post(url, json={'sender': sender, 'recipient': recipient, 'amount': amount, 'signature': signature})
                        if response.status_code == 400 or response.status_code == 500:
                            print('transaction failed, resolve please')
                            return False    
                    except requests.exceptions.ConnectionError:
                        continue
            return True
        return False


    def mine_block(self):
        """ Mines a new block
        """
        # make sure we cant mine without valid wallet
        if self.public_key == None:
            # return False For Old Node.py
            return None
        last_block = self.__chain[-1] # shows current last block of blockchain 
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()
        # reward_transaction = {
        #     'sender': 'MINING',
        #     'recipient': owner,
        #     'amount': MINING_REWARD
        # }
        # using ordered dictionary instead
        reward_transaction = Transaction('MINING', self.public_key, '' ,MINING_REWARD)

        # reward_transaction = OrderedDict([('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)])
        copied_transactions = self.__open_transactions[:]
        for tx in copied_transactions:
            if not Wallet.verify_transaction(tx):
                return None
                # return False For Old Node.py
        copied_transactions = self.__open_transactions[:]

        for tx in copied_transactions:
            if not Wallet.verify_transaction(tx):
                return None
        copied_transactions.append(reward_transaction)
        # for key in last_block: # for loop on dictionary only loops over keys
        #     value = last_block[key]
        #     hashed_block = hashed_block + str(value)
        #print(hashed_block)
        block = Block(len(self.__chain), hashed_block, copied_transactions, proof)

        # block = {
        #     'previous_hash': hashed_block,
        #     'index': len(blockchain),
        #     'transactions': copied_transactions,
        #     'proof': proof
        # } # dictionary / we add stringyfied versino here. 
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        for node in self.__peer_nodes:
            url = 'http://{}/broadcast-block'.format(node)
            converted_block = block.__dict__.copy()
            converted_block['transactions'] = [
                tx.__dict__ for tx in converted_block['transactions']]
            try:
                response = requests.post(url, json={'block': converted_block})
                if response.status_code == 400 or response.status_code == 500:
                    print('Block declined, needs resolving')
            except requests.exceptions.ConnectionError:
                continue
        return block


    def add_block(self, block):
        """ Adds a block to chain without mining, to broadcast"""
        
        transactions = [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']]
        proof_is_valid = Verification.valid_proof(transactions[:-1], block['previous_hash'], block['proof'])
        hashes_match = hash_block(self.chain[-1]) == block['previous_hash']
        if not proof_is_valid or not hashes_match:
            return False
        converted_block = Block(block['index'], block['previous_hash'], transactions, block['proof'], block['timestamp'])
        self.__chain.append(converted_block)
        stored_transactions = self.__open_transactions[:]
        for itx in block['transactions']:
            for opentx in stored_transactions:
                if opentx.sender == itx['sender'] and opentx.recipient == itx['recipient'] and opentx.amount == itx['amount'] and opentx.signature == itx['signature']:
                    try:
                        self.__open_transactions.remove(opentx)
                    except ValueError:
                        print('Item was already removed')
        self.save_data()
        return True


    def add_peer_node(self,node):
        """Add new node to peer node set.
        
        Arguments:
            :node: the url to added node"""
        self.__peer_nodes.add(node)
        self.save_data()


    def remove_peer_node(self,node):
        """Removes node to peer node set.
        
        Arguments:
            :node: the url to removed node"""
        self.__peer_nodes.discard(node)
        self.save_data()


    def get_peer_nodes(self):
        """ Returns list of all connected nodes """
        return list(self.__peer_nodes)