from web3 import Web3
from eth_account import Account
import json
import logging
from typing import List
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def transfer_eth(private_keys_file: str, destination_address: str, provider_url: str) -> None:
    """
    Transfer ETH from multiple wallets to a single destination wallet.
    
    Args:
        private_keys_file (str): Path to file containing private keys
        destination_address (str): Destination wallet address
        provider_url (str): Ethereum node URL (e.g. Infura endpoint)
    """
    # Connect to Ethereum network
    w3 = Web3(Web3.HTTPProvider(provider_url))
    
    # Validate destination address
    if not w3.is_address(destination_address):
        raise ValueError("Invalid destination address")
        
    try:
        # Read private keys from file
        with open(private_keys_file, 'r') as f:
            private_keys = [line.strip() for line in f if line.strip()]
            
        logger.info(f"Loaded {len(private_keys)} private keys")
        
        for i, private_key in enumerate(private_keys):
            try:
                # Get account from private key
                account = Account.from_key(private_key)
                address = account.address
                
                # Get balance
                balance = w3.eth.get_balance(address)
                balance_eth = w3.from_wei(balance, 'ether')
                
                if balance == 0:
                    logger.warning(f"Wallet {address} has zero balance, skipping")
                    continue
                
                # Get current gas prices
                gas_price = w3.eth.gas_price
                # Increase gas price by 10% to ensure faster processing
                gas_price = int(gas_price * 1.1)
                
                # Estimate gas limit for the transaction
                gas_estimate = w3.eth.estimate_gas({
                    'from': address,
                    'to': destination_address,
                    'value': balance
                })
                
                # Add 20% buffer to gas estimate
                gas_limit = int(gas_estimate * 1.2)
                
                # Ensure minimum gas limit
                gas_limit = max(gas_limit, 21000)
                
                transaction_fee = gas_price * gas_limit
                
                # Calculate amount to send (balance minus gas fee)
                amount_to_send = balance - transaction_fee
                
                if amount_to_send <= 0:
                    logger.warning(f"Insufficient balance for gas fee in wallet {address}")
                    continue
                
                # Prepare transaction
                transaction = {
                    'nonce': w3.eth.get_transaction_count(address),
                    'to': destination_address,
                    'value': amount_to_send,
                    'gas': gas_limit,
                    'gasPrice': gas_price,
                    'chainId': w3.eth.chain_id
                }
                
                # Sign and send transaction
                signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
                tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                
                logger.info(f"Sent {w3.from_wei(amount_to_send, 'ether')} ETH from {address}")
                logger.info(f"Transaction hash: {tx_hash.hex()}")
                logger.info(f"Gas limit: {gas_limit}, Gas price: {w3.from_wei(gas_price, 'gwei')} gwei")
                
                # Wait for transaction confirmation
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                logger.info(f"Transaction confirmed in block {receipt['blockNumber']}")
                
            except Exception as e:
                logger.error(f"Error processing wallet {i+1}: {str(e)}")
                continue
                
            # Add delay between transactions
            time.sleep(2)
            
    except FileNotFoundError:
        logger.error(f"Private keys file not found: {private_keys_file}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        
def main():
    private_keys_file = "collector.txt"
    destination_address = "0x3EdAD7DFf01D015De2181B5E07D3370a4D6304cE"
    provider_url = "https://apechain.gateway.tenderly.co/2ZfhUMKm9HfON1TNUFbkvV"
    transfer_eth(private_keys_file, destination_address, provider_url)

if __name__ == "__main__": 
    main()