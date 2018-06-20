from uuid import uuid4  # improt unique id

from blockchain import Blockchain
# from verification import Verification
from util.verification import Verification
from wallet import Wallet

port = 5000


class Node:

    def __init__(self):
        #        self.wallet.public_key = str(uuid4())
        self.wallet = Wallet(port)
        # remove all instances of port if not using multiple local blockchains

        # self.wallet.public_key = 'STEFFEN' # remove when wallet works
        # self.blockchain = Blockchain(self.wallet.public_key)
        # generates new chain with unique node id
        self.wallet.create_keys()
        self.blockchain = Blockchain(self.wallet.public_key, port)
        # self.blockchain = Blockchain(self.wallet.public_key)
        # uncomment if not using local blockchain

    def get_transaction_value(self):
        tx_recipient = input('enter the recipient:')
        tx_amount = float(input('Enter Your amount: '))
        return (tx_recipient, tx_amount)  # a tuple

    def get_user_choice(self):
        user_input = input('Your choice: ')
        return user_input

    def print_blockchain_elements(self):
        # output blockchain list / for loop
        for block in self.blockchain.chain:
            print('Block')
            print(block)
        else:
            print('-' * 30)

    def listen_for_input(self):
        # split this while loop up in other function.
        waiting_for_input = True
        # validate letters as well.
        while waiting_for_input:
            print('Please choose: ')
            print('1: add transaction')
            print('2: mine new block')
            print('3: output blockchain')
            print('4: Check transaction validity')
            print('5: Create Wallet')
            print('6: Load Wallet')
            print('7: Save Keys')
            print('h: Manipulate Chain')
            print('0: quit')
            user_choice = self.get_user_choice()
            print(user_choice)
            if user_choice == '1':
                tx_data = self.get_transaction_value()
                recipient, amount = tx_data
                # just add a if to check if success as under
                signature = self.wallet.sign_transaction(
                    self.wallet.public_key, recipient, amount)
                if self.blockchain.add_transaction(
                        recipient,
                        self.wallet.public_key,
                        signature, amount=amount):
                    print('Added transaction successful')
                else:
                    print('transaction failed')
                print('Open Transactions: ' +
                      str(self.blockchain.get_open_transactions()))
            elif user_choice == '2':
                if not self.blockchain.mine_block():
                    print('Mining Failed. Create a wallet')
            elif user_choice == '3':
                print('you picked 3')
                self.print_blockchain_elements()
            # elif user_choice == '4':
            #    print(participants)
            elif user_choice == '4':
                if Verification.verify_transactions(
                        self.blockchain.get_open_transactions(),
                        self.blockchain.get_balance):
                    print('All transactions valid')
                else:
                    print('some invalid transactions')
            # elif user_choice == 'h':
            #     if len(blockchain) >= 1:
            #         blockchain[0] = {
            #             'previous_hash': '',
            #             'index': 0,
            #             'transactions': [{'sender': 'Marco',
            #               'recipient': 'polo', 'amount': 1000}]
            #         }
            #         print('picked h')
            elif user_choice == '5':  # create wallet
                #   self.wallet = Wallet()
                self.wallet.create_keys()
                self.blockchain = Blockchain(self.wallet.public_key, port)
                # self.blockchain = Blockchain(self.wallet.public_key)
            elif user_choice == '6':  # load wallet
                self.wallet.load_keys()
                self.blockchain = Blockchain(self.wallet.public_key, port)
                # self.blockchain = Blockchain(self.wallet.public_key)
            elif user_choice == '7':  # load wallet
                self.wallet.save_keys()
            elif user_choice == '0':
                # break
                waiting_for_input = False
                # break to quit or use continue to exit the loop.
                # continue skips rest of the loop code.
            else:
                print('invalid input')
            if not Verification.verify_chain(self.blockchain.chain):
                self.print_blockchain_elements()
                print('invalid chain')
                break
            print('Balance of {0}: {1:6.2f}'.format(
                self.wallet.public_key,
                self.blockchain.get_balance()))
            # Better formatting by string formatting
        print('Closed!')


if __name__ == '__main__':
    node = Node()
    node.listen_for_input()
