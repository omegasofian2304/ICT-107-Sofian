import os
from web3 import Web3
import json
from dotenv import load_dotenv

load_dotenv()

# ==================== CONFIGURATION ====================
private_key = os.getenv("PRIVATE_KEY")
deployer_address = "0x7fF364D8D14630d16c2217fC6bD66C14E4AC39f5"

# URL de l'image hébergée (IPFS, Imgur, etc.)
# Cette URL sera stockée dans le NFT comme metadata
URI = "https://imgur.com/a/IcicipG"

# Adresse du contrat NFT déployé (fournie dans l'exercice)
contract_address = "0x9A8C8E2EB8F6fA1Bd7EF9161417F64E48bf54225"
# =====================================================

# Connexion au nœud Ethereum CPNV
w3 = Web3(Web3.HTTPProvider("http://10.229.43.182:8545"))
assert w3.is_connected(), "❌ Échec de la connexion au nœud Ethereum"
print("✅ Connecté au nœud Ethereum CPNV")

# Conversion de l'adresse en format checksum
sender_address = w3.to_checksum_address(deployer_address)
contract_address = w3.to_checksum_address(contract_address)

# Charger l'ABI du contrat
with open(r"C:\Users\pn82bby\PycharmProjects\ICT-107-Sofian\nft\SimpleMintContract.abi", "r") as abi_file:
    contract_abi = json.load(abi_file)

# Créer l'instance du contrat
nft_contract = w3.eth.contract(address=contract_address, abi=contract_abi)

print(f"\n📋 Informations du contrat :")
print(f"   Adresse : {contract_address}")
print(f"   Prix du mint : {nft_contract.functions.mintPrice().call() / 10 ** 18} ETH")
print(f"   Total Supply : {nft_contract.functions.totalSupply().call()}")
print(f"   Max Supply : {nft_contract.functions.maxSupply().call()}")
print(f"   Mint activé : {nft_contract.functions.isMintEnabled().call()}")

# Vérifier combien de NFT l'adresse a déjà minté
minted_count = nft_contract.functions.mintedWallets(sender_address).call()
print(f"   NFTs déjà mintés par votre adresse : {minted_count}")

# Vérifier le solde de l'adresse
balance = w3.eth.get_balance(sender_address)
print(f"\n💰 Solde de votre wallet : {w3.from_wei(balance, 'ether')} ETH")

# ==================== MINT DU NFT ====================
print("\n🎨 Préparation du mint du NFT...")

# Récupérer le nonce (nombre de transactions de l'adresse)
nonce = w3.eth.get_transaction_count(sender_address)

# Prix du mint en ETH
mint_price_eth = 0.05

# Construire la transaction de mint
mint_txn = nft_contract.functions.mint(URI).build_transaction({
    "chainId": 32383,  # ID de la blockchain CPNV
    "gas": 2000000,
    "gasPrice": w3.to_wei("10", "gwei"),
    "value": w3.to_wei(mint_price_eth, "ether"),
    "nonce": nonce
})

# Signer la transaction avec la clé privée
signed_mint_txn = w3.eth.account.sign_transaction(mint_txn, private_key)

try:
    # Test préalable pour vérifier que la transaction peut passer
    # (évite de perdre des frais de gas si la transaction va échouer)
    print("🔍 Vérification préalable...")
    mint_check = nft_contract.functions.mint(URI).call({
        "from": sender_address,
        "value": w3.to_wei(mint_price_eth, "ether")
    })
    print("✅ Vérification réussie, la transaction devrait passer")

    # Envoyer la transaction signée
    print("📤 Envoi de la transaction de mint...")
    mint_tx_hash = w3.eth.send_raw_transaction(signed_mint_txn.raw_transaction)
    print(f"✅ Transaction envoyée : {mint_tx_hash.hex()}")
    print(f"   Vous pouvez suivre la transaction sur l'explorateur de blocs")

    # Attendre la confirmation de la transaction
    print("⏳ Attente de la confirmation...")
    mint_receipt = w3.eth.wait_for_transaction_receipt(mint_tx_hash)
    print(f"✅ Transaction confirmée dans le bloc {mint_receipt.blockNumber}")

    # Récupérer le token ID minté
    token_id = nft_contract.functions.totalSupply().call()
    print(f"\n🎉 NFT minté avec succès !")
    print(f"   Token ID : {token_id}")
    print(f"   Propriétaire : {sender_address}")
    print(f"   Metadata URI : {URI}")

    # Vérifier le propriétaire du token
    owner = nft_contract.functions.ownerOf(token_id).call()
    print(f"   Vérification : Le propriétaire du token #{token_id} est {owner}")

except Exception as e:
    print(f"\n❌ Une erreur est survenue : {str(e)}")
    print("\n💡 Vérifications à faire :")
    print("   - Le mint est-il activé ? (isMintEnabled doit être true)")
    print("   - Avez-vous déjà minté un NFT ? (limite : 1 par wallet)")
    print("   - Avez-vous assez d'ETH ? (minimum 0.05 ETH + frais de gas)")
    print("   - Votre clé privée est-elle correcte ?")
    print("   - Le maxSupply est-il atteint ?")