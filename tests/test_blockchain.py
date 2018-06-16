import sys
sys.path.insert(0,'../')
import simple_chain
def test_proof_of_work():
    demo_blockchain = simple_chain.Blockchain()
    demo_blockchain.proof_of_work(100)
test_proof_of_work()
    
