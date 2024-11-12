from web3 import Web3
from config import RPC, CONTRACT_ADDRESS, RECIEVER_ADDRESS
from abi import ABI

w3 = Web3(Web3.HTTPProvider(RPC))

contract_address = w3.to_checksum_address(CONTRACT_ADDRESS)
reciever_address = w3.to_checksum_address(RECIEVER_ADDRESS)

contract = w3.eth.contract(address=contract_address, abi=ABI)

def readKeys(filepath):
    with open(filepath, 'r') as file:
        privateKeys = file.read().splitlines()
    return privateKeys

def createAccounts(privateKeys):
    accounts = []
    for privateKey in privateKeys:
        account = w3.eth.account.from_key(privateKey)
        accounts.append(account)
    return accounts

def parseWalletBalance(account):
    tokens = contract.functions.tokensOfOwner(account.address).call()
    return tokens

def sendNft(tokens, account):
    for token in tokens:
        nonce = w3.eth.get_transaction_count(account.address)
        transaction = contract.functions.safeTransferFrom(
            account.address, reciever_address, token
            ).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'chainId': 33139,
            'value': 0,
            'gasPrice': w3.eth.gas_price
        })

        try:
            transaction['gas'] = w3.eth.estimate_gas(transaction)
        except Exception as e:
            print(f"Error: {e} while sending token {token}, from wallet {account.address}")
            continue
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key=account.key)
        
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Token {token} successfully transfered from address {account.address}")

def main():
    addresses = readKeys("pr.txt")
    accounts = createAccounts(addresses)
    for account in accounts:
        tokens = parseWalletBalance(account)
        sendNft(tokens, account)

if __name__ == "__main__":
    main()