import functools
import hashlib
import json
from collections import OrderedDict

# define chain
MINING_REWARD = 10 # global constant 

genesis_block = {
        'previous_hash': '',
        'index': 0,
        'transactions': [],
        'proof': 100
}
blockchain = [genesis_block] # list
open_transactions = [] # list of pending transactions
owner = 'Owner'
participants = {'Owner'}


def hash_block(block):
    """ returns hash block
    
    Arguments: 
        :block: The Block That Will Be Hashed
    """
    return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()
#    return '-'.join([str(block[key]) for key in block])
    # use sort_keys to true to sort keys before hashing


def valid_proof(transactions, last_hash, proof):
    """ Checks if new hash is valid

    Arguments: 
        :transactions:
        :last_hash:
        :proof: proof number / nonce
    """
    guess = (str(transactions) + str(last_hash) + str(proof)).encode() # concat a string
    guess_hash = hashlib.sha256(guess).hexdigest() # guessing if our guess is same as hash
    print(guess_hash)
    return guess_hash[0:2] == '00' # checking the leading zeros, if it is really a hash difficulty change
    # just add zeros to increase difficulty 

def proof_of_work():
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1    
    return proof


def get_balance(participant):
    tx_sender = [[tx['amount'] for tx in block['transactions'] if tx['sender'] == participant] for block in blockchain]
    # need to get open transactions sent using List Comprehension
    open_tx_sender = [tx['amount'] for tx in open_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)
    amount_sent = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
    # above is simpler reduce of below video #94
    # amount_sent = 0
    # for tx in tx_sender:
    #     if len(tx) > 0:
    #         amount_sent += tx[0]
    tx_recipient = [[tx['amount'] for tx in block['transactions'] if tx['recipient'] == participant] for block in blockchain]
    amount_received = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)
    # amount_received = 0
    # for tx in tx_recipient:
    #     if len(tx) > 0:
    #         amount_received += tx[0]
    return amount_received - amount_sent


# Get last blockchain value function
def get_last_blockchain_value():
    """ Returns last blockchain value 
    
    Arguments: none
    """
    if len(blockchain) < 1:
        return None # checking lenght of list
    return blockchain[-1]


# verifying transactions.
def verify_transaction(transaction):
    sender_balance = get_balance(transaction['sender'])
    if sender_balance >= transaction['amount']:
        return True
    else: 
        return False

    # can also write as return sender_balance => transaction['amount]
    # since it just returns true or false. 


# value function
def add_transaction(recipient, sender=owner, amount=1.0):
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

    # using a ordered dictionary instead
    # our key value pair becomes tuples instead
    transaction = OrderedDict([('sender', sender), ('recipient', recipient), ('amount', amount)])
    if verify_transaction(transaction): # if verify transaction successds then do following
        open_transactions.append(transaction) # storing above transactions 
    #    blockchain.append([last_transaction,value])
        participants.add(sender)
        participants.add(recipient)
        return True
    return False


def mine_block():
    """ Mines a new block
    """
    last_block = blockchain[-1] # shows current last block of blockchain 
    hashed_block = hash_block(last_block)
    proof = proof_of_work()
    # reward_transaction = {
    #     'sender': 'MINING',
    #     'recipient': owner,
    #     'amount': MINING_REWARD
    # }
    # using ordered dictionary instead
    reward_transaction = OrderedDict([('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)])
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
    # for key in last_block: # for loop on dictionary only loops over keys
    #     value = last_block[key]
    #     hashed_block = hashed_block + str(value)
    #print(hashed_block)
    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': copied_transactions,
        'proof': proof
    } # dictionary / we add stringyfied versino here. 
    blockchain.append(block)
    return True # sets open_transactions to blank


def get_transaction_value():
    tx_recipient = input('enter the recipient:') 
    tx_amount = float(input('Enter Your amount: '))
    return (tx_recipient, tx_amount) # a tuple


def get_user_choice():
    user_input = input('Your choice: ')
    return user_input


def print_blockchain_elements():
    # output blockchain list / for loop
    for block in blockchain:
        print('Block')
        print(block)
    else:
        print('-' * 30)


def verify_chain():
    """Verifies blockchain validity"""
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(blockchain[index - 1]):
            return False
        if not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):
            print('proof of work invalid')
            return False
    return True


def verify_transactions():
    return all([verify_transaction(tx) for tx in open_transactions])

    # the above is a list comprehension of whats below
    # using all, checks if all transactions are true. Any would check if at least one is true
    # is_valid = True
    # for tx in open_transactions:
    #     if verify_transaction(tx):
    #         is_valid = True
    #     else:
    #         is_valid = False
    #     return is_valid


waiting_for_input = True

# validate letters as well. 
while waiting_for_input:
    print('Please choose: ')
    print('1: add transaction')
    print('2: mine new block')
    print('3: output blockchain')
    print('4: show participants')
    print('5: Check transaction validity')
    print('h: Manipulate Chain')
    print('0: quit')
    user_choice = get_user_choice()
    print(user_choice)
    if user_choice == '1':
        print('you picked 1')
        tx_data = get_transaction_value()
        recipient, amount = tx_data
        # just add a if to check if success as under
        if add_transaction(recipient, amount=amount):
            print('Added transaction successful')
        else:
            print('transaction failed')
        print('Open Transactions: ' + str(open_transactions))
    elif user_choice == '2':
        if mine_block():
            open_transactions = [] # clears open transactions
    elif user_choice == '3':
        print('you picked 3')
        print_blockchain_elements()
    elif user_choice == '4':
        print(participants)
    elif user_choice == '5':
        if verify_transactions():
            print('All transactions valid')
        else:
            print('some invalid transactions')
    elif user_choice == 'h':
        if len(blockchain) >= 1:
            blockchain[0] = {
                'previous_hash': '',
                'index': 0,
                'transactions': [{'sender': 'Marco', 'recipient': 'polo', 'amount': 1000}]
            }
            print('picked h')
    elif user_choice == '0':
        # break
        waiting_for_input = False 
        # break to quit or use continue to exit the loop. 
        # continue skips rest of the loop code. but does not exit the loop
    else: 
        print('invalid input')
    if not verify_chain():
        print_blockchain_elements()
        print('invalid chain')
        break
    print('Balance of {0}: {1:6.2f}'.format('Owner', get_balance('Owner')))
    #Better formatting by string formatting
print('Closed!')

# print(blockchain)
