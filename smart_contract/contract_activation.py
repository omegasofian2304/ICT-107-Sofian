from dotenv import load_dotenv
from web3 import Web3
import os
import json

# ==========================================================

# CONFIGURATION

# ==========================================================

load_dotenv()

# URL RPC de la blockchain privée CPNV

RPC_URL = "http://10.229.43.182:8545"

# Adresse du compte expéditeur

SENDER_ADDRESS = "0x7fF364D8D14630d16c2217fC6bD66C14E4AC39f5"

# Clé privée

PRIVATE_KEY = os.getenv("PRIVATE_KEY")

contract_address = "0x52e3B9942CAD6e95cBab4a2D18AB0311D3d389DC"

w3 = Web3(Web3.HTTPProvider(RPC_URL))

if w3.is_connected():

    print("✅ Connecté à la blockchain")

else:

    print("❌ Connexion échouée")

    exit()

account = w3.eth.account.from_key(PRIVATE_KEY)

with open("HusseinSofianContract.abi", "r") as abi_file:
    abi = json.load(abi_file)

# Créer instance du contrat
contract = w3.eth.contract(
    address=contract_address,
    abi=abi
)

# Build transaction
tx = contract.functions.toggleIsMintEnabled().build_transaction({
    "from": account.address,
    "nonce": w3.eth.get_transaction_count(account.address),
    "gas": 100000,
    "gasPrice": w3.eth.gas_price,
})

# Sign and send
signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

print("Transaction hash:", tx_hash.hex())

# Wait for confirmation
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Block:", receipt.blockNumber)

# Verify state
enabled = contract.functions.isMintEnabled().call()
print("isMintEnabled =", enabled)
