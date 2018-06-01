from uuid import uuid4 # improt unique id

from blockchain import Blockchain
from verification import Verification

class Node:

    def __init__(self):
#        self.id = str(uuid4())
        self.id = 'STEFFEN'
        self.blockchain = Blockchain(self.id) #generates new chain with unique node id

    def get_transaction_value(self):
        tx_recipient = input('enter the recipient:') 
        tx_amount = float(input('Enter Your amount: '))
        return (tx_recipient, tx_amount) # a tuple


    def get_user_choice(self):
        user_input = input('Your choice: ')
        return user_input


    def print_blockchain_elements(self):
        # output blockchain list / for loop
        for block in self.blockchain.get_chain():
            print('Block')
            print(block)
        else:
            print('-' * 30)

    def listen_for_input(self):
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
            user_choice = self.get_user_choice()
            print(user_choice)
            if user_choice == '1':
                print('you picked 1')
                tx_data = self.get_transaction_value()
                recipient, amount = tx_data
                # just add a if to check if success as under
                if self.blockchain.add_transaction(recipient,self.id, amount=amount):
                    print('Added transaction successful')
                else:
                    print('transaction failed')
                print('Open Transactions: ' + str(self.blockchain.get_open_transactions()))
            elif user_choice == '2':
                self.blockchain.mine_block()
            elif user_choice == '3':
                print('you picked 3')
                self.print_blockchain_elements()
            # elif user_choice == '4':
            #    print(participants)
            elif user_choice == '4':
                if Verification.verify_transactions(self.blockchain.get_open_transactions(), self.blockchain.get_balance):
                    print('All transactions valid')
                else:
                    print('some invalid transactions')
            # elif user_choice == 'h':
            #     if len(blockchain) >= 1:
            #         blockchain[0] = {
            #             'previous_hash': '',
            #             'index': 0,
            #             'transactions': [{'sender': 'Marco', 'recipient': 'polo', 'amount': 1000}]
            #         }
            #         print('picked h')
            elif user_choice == '0':
                # break
                waiting_for_input = False 
                # break to quit or use continue to exit the loop. 
                # continue skips rest of the loop code. but does not exit the loop
            else: 
                print('invalid input')
            if not Verification.verify_chain(self.blockchain.get_chain()):
                self.print_blockchain_elements()
                print('invalid chain')
                break
            print('Balance of {0}: {1:6.2f}'.format(self.id, self.blockchain.get_balance()))
            #Better formatting by string formatting
        print('Closed!')

node = Node()
node.listen_for_input()