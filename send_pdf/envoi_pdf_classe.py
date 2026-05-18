from web3 import Web3
import json
import os

from dotenv import load_dotenv
# ==========================================================

# CONFIGURATION

# ==========================================================

load_dotenv()

# URL RPC de la blockchain privée CPNV

RPC_URL = "http://10.229.43.182:8545"

# Adresse du compte expéditeur

SENDER_ADDRESS = "0x7fF364D8D14630d16c2217fC6bD66C14E4AC39f5"

# Clé privée (⚠ À améliorer !)

PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# Métadonnées de ton fichier PDF
GITHUB_URL = "https://github.com/omegasofian23/ICT-107-Sofian/file_to_hash/sofian_hussein.pdf"
FILE_HASH = "e7f07f5f683b2d997f529387eaa41304f810db7cc6abe041142edac18afc0144"

# ==========================================================

# CONNEXION À LA BLOCKCHAIN

# ==========================================================


w3 = Web3(Web3.HTTPProvider(RPC_URL))

if w3.is_connected():

    print("✅ Connecté à la blockchain")

else:

    print("❌ Connexion échouée")

    exit()


def prepare_metadata(github_url, file_hash):
    """
    Prépare les métadonnées au format JSON et les convertit en hexadécimal
    """
    # Créer un dictionnaire avec url et hash
    metadata = {
        "url": github_url,
        "hash": file_hash
    }

    # Convertir en JSON string
    json_str = json.dumps(metadata)

    # Encoder en bytes (UTF-8)
    metadata_bytes = json_str.encode('utf-8')

    # Convertir en hexadécimal
    metadata_hex = metadata_bytes.hex()

    # Ajouter le préfixe '0x'
    return '0x' + metadata_hex

# ==========================================================

# LECTURE DES ADRESSES

# ==========================================================

def lire_adresses(fichier):
    """

    Lire les adresses Ethereum depuis un fichier texte

    Retourne une liste d’adresses

    """

    adresses = []

    with open(fichier, "r") as f:

        for ligne in f:

            adresse = ligne.strip()

            # Vérifier que l’adresse est valide

            if Web3.is_address(adresse):
                adresses.append(adresse)

    return adresses


# ==========================================================

# AFFICHER LES SOLDES

# ==========================================================

def afficher_soldes(adresses):
    """

    Affiche le solde de chaque adresse

    """

    for adresse in adresses:
        balance_wei = w3.eth.get_balance(adresse)

        balance_eth = w3.from_wei(balance_wei, "ether")

        print(f"{adresse} : {balance_eth} ETH")


# ==========================================================

# ENVOI DE TRANSACTION

# ==========================================================

def ecrire_metadata_blockchain(metadata_hex, nonce):
    """

    Construit, signe et envoie une transaction

    """

    transaction = {
        'from': SENDER_ADDRESS,
        'to': '0x0000000000000000000000000000000000000000',
        'value': 0,
        'gas': 200000,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': nonce,
        'chainId': 32383,
        'data': metadata_hex
    }

    # Signature de la transaction

    signed_tx = w3.eth.account.sign_transaction(transaction, PRIVATE_KEY)

    # Envoi sur le réseau

    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    return tx_hash.hex()


# ==========================================================

# PROGRAMME PRINCIPAL

# ==========================================================

def main():
    print("\n=== Préparation des métadonnées ===")

    # Préparer les métadonnées en hex
    metadata_hex = prepare_metadata(GITHUB_URL, FILE_HASH)
    print(f"Métadonnées (hex) : {metadata_hex[:50]}...")  # Afficher les 50 premiers caractères

    # Récupérer le nonce
    nonce = w3.eth.get_transaction_count(SENDER_ADDRESS)
    print(f"Nonce actuel : {nonce}")

    print("\n=== Envoi de la transaction ===")

    try:
        tx_hash = ecrire_metadata_blockchain(metadata_hex, nonce)
        print(f"Transaction envoyée !")
        print(f"Hash de transaction : {tx_hash}")
        print(f"\nNote ce hash, tu en auras besoin pour récupérer les données !")

    except Exception as e:
        print(f"Erreur : {e}")


if __name__ == "__main__":
    main()