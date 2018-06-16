import hashlib
import json
from time import time
from urllib.parse import urlparse
import requests

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        #Genesis Block 1:1-2 - In the beginning, God created the heavens and earth.
        #the earth being untamed and shapeless, God said,
        #"let there be the genesis block!"
        self.new_block(previous_hash=1,proof=100)

    def proof_of_work(self, last_proof):
        """
        Description
        -
        Find a number p' such that hash(pp') contains leading 4 zeroes
        where p is the previous p'

        Parameters
        -
        last_proof: <int> the previous proof

        Return
        -
        proof: <int> that new proof
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof+=1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        desc
        ---
        checks the validity of a proof

        params
        ---
        last_proof: <int> the proof from the last block
        proof: <int> speculative proof

        Returns
        ---
        <bool>
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == '0000'

    def new_block(self, proof, previous_hash=None):
        """
        Desc
        ---
        create a new block in the chain
        Params
        ---
        proof: <int> proof given by the proof of work algorithm
        previous_hash: <str> hash of the previous block
        """
        block = {
            'index' : len(self.chain) + 1,
            'timestamp' : time(),
            'transactions' : self.current_transactions,
            'proof' : proof,
            'previous_hash' : previous_hash or self.hash_block(self.chain[-1])
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Desc
        ---
        creates a new transaction that will be place into the next mined block

        Params
        ---
        sender: str
        address of sender
        recipient: str
        address of recipient
        amount: float
        amount exchanged
        """
        self.current_transactions.append({'sender': sender,
                                          'recipient':recipient,
                                          'amount':amount})
        return self.last_block['index'] + 1

    @staticmethod
    def hash_block(block):
        """
        Desc: creates SHA-256 hash of block
        Params:
        block: <dict> a block
        Returns:
        hash_string: <str> a hash string
        """
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        #returns last block on the chain
        return self.chain[-1]

    def register_node(self, address):
        """
        Description
        ---
        register unique nodes and save to the chain
        
        parameters
        ---
        address: <str>
        address of node taht will be parsed
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """
        Description
        ---
        checks the validity of a chain by testing the proofs and the hashes

        Parameters
        ---
        chain: <list>
        a list object with json blocks 

        Returns: <bool>
        is the chain valid?
        """
      
        for i in range(1, len(chain)):#if you get some index error check here
            #verify validity of hashes for blocks
            if chain[i]['previous_hash'] != self.hash_block(chain[i-1]):
                return False
            
            #verify block proofs
            if not self.valid_proof(chain[i-1]['proof'], chain['proof']):
                return False

        return True

    def resolve_conflicts(self):
        neighbors = self.nodes
        new_chain = None
        max_length = len(self.chain)

        for node in self.nodes:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False
        

        
