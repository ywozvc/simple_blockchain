import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4
import requests
from flask import Flask, jsonify, request
import simple_chain as bc

app = Flask(__name__)
node_identifier = str(uuid4()).replace('-','')

blockchain = bc.Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)
    blockchain.new_transaction(sender = 0, recipient=node_identifier,amount=1)
    previous_hash = blockchain.hash_block(last_block)
    block = blockchain.new_block(proof,previous_hash)

    response = {
        'message' : 'new block forge bruh',
        'index' : block['index'],
        'transactions' : block['transactions'],
        'proof' : block['proof']
    }
    return jsonify(response), 201 #request fulfilled object created

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = requests.get_json()
    required = ['sender', 'recipient','amount']
    if not all(k in values for k in required):
        return 'missing values', 412 #precondition failed
    else:
        index = blockchain.new_transaction(values['sender'],values['recipient'],values['amount'])
        response = {'message' : f'transaction will be added to block {index}'}
        return jsonify(response), 201 #fulfill and something created

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {"chain" : blockchain.chain,
                "length" : len(blockchain.chain)}
    return jsonify(response), 200 #ok

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = requests.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return "need nodes", 400
    for node in nodes:
        blockchain.register_node(node)
    response = {'message': 'new nodes added',
                'total_nodes' : list(blockchain.nodes)}
    return jsonify(response)

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {'message' : 'our chain was replaced',
                    'new chain' : blockchain.chain}
    else:
        response = {'message': 'chain authoritative',
                    'chain' : blockchain.chain}

    return jsonify(response)

if(__name__ == "__main__"):
    app.run(host='0.0.0.0', port=5000)
