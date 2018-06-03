from flask import Flask, jsonify
from flask_cors import CORS

from wallet import Wallet
from blockchain import Blockchain

app = Flask(__name__)
wallet = Wallet()
blockchain = Blockchain(wallet.public_key)
CORS(app) #wrap app with CORS to allow access 


@app.route('/', methods=['GET']) # decorator to create route
def get_ui():
    return 'Working? Yes'


@app.route('/mine', methods=['POST'])
def mine():
    block =  blockchain.mine_block()
    if block != None:
        dict_block = block.__dict__.copy() # return block to dictionary
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']] # list comprehension
        response = {
            'message': 'Block added',
            'block': dict_block
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Adding block failed',
            'wallet_set_up': wallet.public_key != None
        }
        return jsonify(response), 500


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_snapshot = blockchain.chain
    dict_chain = [block.__dict__.copy() for block in chain_snapshot] # list comprehension that converts chain to dictionary per block
    for dict_block in dict_chain:
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
    return jsonify(dict_chain), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000) #localhost port 3000
