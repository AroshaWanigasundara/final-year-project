import subprocess
import json
from web3 import Web3

def model_upload(fileName):
    js_file_path = './web3-storage-quickstart/put-files.js'

    command = ['node', js_file_path, json.dumps(fileName)]

    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        result = output.decode().strip()
        #print("JavaScript function executed successfully.")
        print("Local models CID:", result)
    except subprocess.CalledProcessError as e:
        print("Error executing JavaScript function:", e.output.decode())

    return result

def get_cid_of_data(iteration):
    js_file_path = './web3-storage-quickstart/read_cid.js'

    command = ['node', js_file_path, json.dumps(iteration)]

    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        result = output.decode().strip()
        #print("JavaScript function executed successfully.")
        print("Global model CID:", result)
    except subprocess.CalledProcessError as e:
        print("Error executing JavaScript function:", e.output.decode())

    return result

def get_cid_of_data_ar1():
    js_file_path = './web3-storage-quickstart/read_cid_ar1.js'

    command = ['node', js_file_path]

    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        result = output.decode().strip()
        #print("JavaScript function executed successfully.")
        print("Aggregation data CID:", result)
    except subprocess.CalledProcessError as e:
        print("Error executing JavaScript function:", e.output.decode())

    return result

def client_model_retrieve(cid):
    js_file_path = './web3-storage-quickstart/retrieve.js'

    command = ['node', js_file_path, json.dumps(cid)]

    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        result = output.decode().strip()
        #print("JavaScript function executed successfully.")
        print(result)
    except subprocess.CalledProcessError as e:
        print("Error executing JavaScript function:", e.output.decode())

    return result


def add_block(content_ID):
    # Connect to the Ethereum network using Infura
    infura_url = 'https://sepolia.infura.io/v3/edbaf363f322439e9b71df83782130d1'
    web3 = Web3(Web3.HTTPProvider(infura_url))

    # Set up the contract ABI and address
    contract_address = "0x4FEC4A9422a3ACc9e36b8f2A07F53B44ab4f1016"
    with open('contract_abi.json', 'r') as f:
        contract_abi = json.load(f)

    # Load the contract
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)

    # Get the function signature for saveIPFSHash
    function_signature = contract.encodeABI(fn_name='recordTransaction', args=[content_ID])

    # Build the transaction
    nonce = web3.eth.get_transaction_count('0x2E0d82d63Dd2C98AB40A2e1b8C6404E57618A0e3')
    transaction = {
        'to': contract_address,
        'data': function_signature,
        'from': '0x2E0d82d63Dd2C98AB40A2e1b8C6404E57618A0e3',
        'gas': 3000000,
        #'gas': web3.eth.estimate_gas({'to': contract_address, 'data': function_signature}),
        'gasPrice': web3.eth.gas_price,
        'nonce': nonce,
    }

    # Sign and send the transaction
    signed_txn = web3.eth.account.sign_transaction(transaction, private_key='3a244a14229e67117deadebf464c4744be018b6c413b52445c23b09107f36386')
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    print("Content ID saved successfully!")


def view_block(index_ID):

    w3 = Web3(Web3.HTTPProvider("https://sepolia.infura.io/v3/edbaf363f322439e9b71df83782130d1"))

    contract_address = "0xeA4D9A0F8D24c1A906e8aa3259eB1E2ba1732947"
    with open('contract_abi.json', 'r') as f:
        contract_abi = json.load(f)

    contract_instance = w3.eth.contract(address=contract_address, abi=contract_abi)
    result = contract_instance.functions.getIPFSHash(index_ID).call()
    print(result)


def off_chain_request(content_ID):

    MAX_RETRIES = 5

    for i in range(MAX_RETRIES):

        try:

            # existing transaction code 

            # Connect to the Ethereum network using Infura
            infura_url = 'https://sepolia.infura.io/v3/edbaf363f322439e9b71df83782130d1'
            web3 = Web3(Web3.HTTPProvider(infura_url))

            # Set up the contract ABI and address
            #contract_address = "0x89Cf7FC0bE35066A80cC03E8Cf3DF9878cB4A9ad"
            #contract_address = "0xf5AaE5651228e790658A7da6af0C27B2a5adD6aF"
            contract_address = "0x65b895c40D72f9ff17eC9D0aa4B6E50680568D70"
            with open('off_chain_contract_abi.json', 'r') as f:
                contract_abi = json.load(f)

            # Load the contract
            contract = web3.eth.contract(address=contract_address, abi=contract_abi)

            # Get the function signature for saveIPFSHash
            #function_signature = contract.encodeABI(fn_name='saveIPFSHash', args=[index,content_ID,name])
            function_signature = contract.encodeABI(fn_name='requestCidOfAggregationData', args=[content_ID])

            # Build the transaction
            #nonce = web3.eth.get_transaction_count('0x2E0d82d63Dd2C98AB40A2e1b8C6404E57618A0e3')
            nonce = web3.eth.get_transaction_count('0xf76e6727c197D1bc762eC2EAfa516C250482a2E3')
            transaction = {
                'to': contract_address,
                'data': function_signature,
                #'from': '0x2E0d82d63Dd2C98AB40A2e1b8C6404E57618A0e3',
                'from': '0xf76e6727c197D1bc762eC2EAfa516C250482a2E3',
                'gas': 140000,
                #'gas': web3.eth.estimate_gas({'to': contract_address, 'data': function_signature}),
                'gasPrice': web3.eth.gas_price,
                'nonce': nonce,
            }

            # Sign and send the transaction
            #signed_txn = web3.eth.account.sign_transaction(transaction, private_key='3a244a14229e67117deadebf464c4744be018b6c413b52445c23b09107f36386')
            signed_txn = web3.eth.account.sign_transaction(transaction, private_key='87b41d520163141e94e01e41ab3728786d72dd3bce1d2fde4ad262ced951320c')
            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

            # Transaction succeeded, exit loop
            break

        except Exception as e:

            print(f"Error: {e}")  
            print(f"Retrying, attempt {i+1}/{MAX_RETRIES}")

    if i == MAX_RETRIES - 1:
        print("Transaction failed after max retries")
    else:
        print("Off-chain computation request succeeded")

def off_chain_request_full(content_ID):

    MAX_RETRIES = 5

    for i in range(MAX_RETRIES):

        try:

            # existing transaction code 

            # Connect to the Ethereum network using Infura
            infura_url = 'https://sepolia.infura.io/v3/edbaf363f322439e9b71df83782130d1'
            web3 = Web3(Web3.HTTPProvider(infura_url))

            # Set up the contract ABI and address
            contract_address = "0x89Cf7FC0bE35066A80cC03E8Cf3DF9878cB4A9ad"
            #contract_address = "0xf5AaE5651228e790658A7da6af0C27B2a5adD6aF"
            #contract_address = "0x65b895c40D72f9ff17eC9D0aa4B6E50680568D70"
            with open('off_chain_contract_abi2.json', 'r') as f:
                contract_abi = json.load(f)

            # Load the contract
            contract = web3.eth.contract(address=contract_address, abi=contract_abi)

            # Get the function signature for saveIPFSHash
            #function_signature = contract.encodeABI(fn_name='saveIPFSHash', args=[index,content_ID,name])
            function_signature = contract.encodeABI(fn_name='requestCidOfAggregationData', args=[content_ID])

            # Build the transaction
            nonce = web3.eth.get_transaction_count('0x2E0d82d63Dd2C98AB40A2e1b8C6404E57618A0e3')
            #nonce = web3.eth.get_transaction_count('0xf76e6727c197D1bc762eC2EAfa516C250482a2E3')
            transaction = {
                'to': contract_address,
                'data': function_signature,
                'from': '0x2E0d82d63Dd2C98AB40A2e1b8C6404E57618A0e3',
                #'from': '0xf76e6727c197D1bc762eC2EAfa516C250482a2E3',
                'gas': 140000,
                #'gas': web3.eth.estimate_gas({'to': contract_address, 'data': function_signature}),
                'gasPrice': web3.eth.gas_price,
                'nonce': nonce,
            }

            # Sign and send the transaction
            signed_txn = web3.eth.account.sign_transaction(transaction, private_key='3a244a14229e67117deadebf464c4744be018b6c413b52445c23b09107f36386')
            #signed_txn = web3.eth.account.sign_transaction(transaction, private_key='87b41d520163141e94e01e41ab3728786d72dd3bce1d2fde4ad262ced951320c')
            tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

            # Transaction succeeded, exit loop
            break

        except Exception as e:

            print(f"Error: {e}")  
            print(f"Retrying, attempt {i+1}/{MAX_RETRIES}")

    if i == MAX_RETRIES - 1:
        print("Transaction failed after max retries")
    else:
        print("Off-chain computation request succeeded")

