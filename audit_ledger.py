import json
import hashlib
import os
from datetime import datetime

LEDGER_FILE = 'mongo_audit_ledger.json'

def get_ledger():
    if not os.path.exists(LEDGER_FILE):
        return []
    with open(LEDGER_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_ledger(chain):
    with open(LEDGER_FILE, 'w') as f:
        json.dump(chain, f, indent=4)

def append_ballot_receipt(election_id, ballot_token, ranked_payload):
    chain = get_ledger()
    
    # Sort payload to ensure deterministic hashing
    payload_str = json.dumps(sorted(ranked_payload, key=lambda x: x[1]), sort_keys=True)
    vote_data_hash = hashlib.sha256(payload_str.encode()).hexdigest()
    
    prev_hash = chain[-1]['curr_hash'] if chain else "0" * 64
    
    block = {
        "index": len(chain) + 1,
        "timestamp": datetime.now().isoformat(),
        "election_id": election_id,
        "ballot_token": ballot_token,
        "vote_data_hash": vote_data_hash,
        "prev_hash": prev_hash,
    }
    
    block_string = json.dumps(block, sort_keys=True)
    block['curr_hash'] = hashlib.sha256(block_string.encode()).hexdigest()
    
    chain.append(block)
    save_ledger(chain)
    return block

def verify_chain_integrity():
    chain = get_ledger()
    if not chain:
        return True, "Ledger is empty."
    
    for i in range(1, len(chain)):
        prev_block = chain[i-1]
        curr_block = chain[i]
        
        if curr_block['prev_hash'] != prev_block['curr_hash']:
            return False, f"Broken link at block {curr_block['index']}"
            
        temp_block = curr_block.copy()
        del temp_block['curr_hash']
        recalc_hash = hashlib.sha256(json.dumps(temp_block, sort_keys=True).encode()).hexdigest()
        if recalc_hash != curr_block['curr_hash']:
            return False, f"Data tampered at block {curr_block['index']}"
            
    return True, "Chain intact. Cryptographic ledger is valid."