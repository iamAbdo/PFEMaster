import os
import requests
from nacl import public, encoding, exceptions as nacl_exceptions
from nacl.secret import SecretBox
from nacl.utils import random
import argon2
import nacl.bindings as sodium
from tkinter import messagebox, simpledialog
from utils.auth_state import get_jwt_token_global

def generate_user_keypair(password: str, user_id: str) -> tuple[bytes, bytes]:
    """Generate keypair specific to user using their ID as salt"""
    # Use user ID as part of salt for user-specific keys
    salt = f"user_{user_id}_salt".encode()
    
    # Derive 32-byte seed using Argon2
    seed = argon2.low_level.hash_secret_raw(
        secret=password.encode(),
        salt=salt,
        time_cost=3,
        memory_cost=65536,
        parallelism=4,
        hash_len=32,
        type=argon2.low_level.Type.ID
    )
    
    # Generate Ed25519 key pair from seed
    public_key, private_key = sodium.crypto_sign_seed_keypair(seed)
    
    # Convert to X25519 keys for encryption
    x25519_private = sodium.crypto_sign_ed25519_sk_to_curve25519(private_key)
    x25519_public = sodium.crypto_sign_ed25519_pk_to_curve25519(public_key)
    
    return (x25519_private, x25519_public)

def encrypt_file(filepath):
    """Encrypt a file using user's password-derived key"""
    jwt_token = get_jwt_token_global()
    if not jwt_token:
        messagebox.showerror("Erreur", "Vous devez être connecté pour chiffrer des fichiers")
        return
    
    # Get user password
    password = simpledialog.askstring("Mot de passe", "Entrez votre mot de passe pour le chiffrement:", show='*')
    if not password:
        return
    
    try:
        # Get user info from backend
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.get('https://127.0.0.1:5000/api/user/profile', headers=headers, verify=False)
        
        if response.status_code != 200:
            messagebox.showerror("Erreur", "Impossible de récupérer les informations utilisateur")
            return
        
        user_data = response.json()
        user_id = str(user_data['id'])
        
        # Generate user-specific keypair
        private_key, public_key = generate_user_keypair(password, user_id)
        
        # Encrypt the file
        box = SecretBox(private_key)
        with open(filepath, 'rb') as f:
            plaintext = f.read()

        nonce = random(SecretBox.NONCE_SIZE)
        ciphertext = box.encrypt(plaintext, nonce)

        # Save encrypted file with .enc extension
        encrypted_path = filepath + '.enc'
        with open(encrypted_path, 'wb') as f:
            f.write(ciphertext)

        # Delete the original file after successful encryption
        os.remove(filepath)

        messagebox.showinfo("Succès", f"Fichier chiffré avec succès!\nSauvegardé comme: {os.path.basename(encrypted_path)}\nFichier original supprimé.")
        
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du chiffrement: {str(e)}")

def decrypt_file(filepath):
    """Decrypt a file using user's password-derived key"""
    jwt_token = get_jwt_token_global()
    if not jwt_token:
        messagebox.showerror("Erreur", "Vous devez être connecté pour déchiffrer des fichiers")
        return
    
    # Get user password
    password = simpledialog.askstring("Mot de passe", "Entrez votre mot de passe pour le déchiffrement:", show='*')
    if not password:
        return
    
    try:
        # Get user info from backend
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.get('https://127.0.0.1:5000/api/user/profile', headers=headers, verify=False)
        
        if response.status_code != 200:
            messagebox.showerror("Erreur", "Impossible de récupérer les informations utilisateur")
            return
        
        user_data = response.json()
        user_id = str(user_data['id'])
        
        # Generate user-specific keypair
        private_key, public_key = generate_user_keypair(password, user_id)
        
        # Decrypt the file
        box = SecretBox(private_key)
        with open(filepath, 'rb') as f:
            encrypted = f.read()

        # Decrypt the message (nonce is included in the encrypted message)
        plaintext = box.decrypt(encrypted)

        # Save decrypted file with original filename (remove .enc extension)
        original_path = filepath.replace('.enc', '')
        with open(original_path, 'wb') as f:
            f.write(plaintext)

        # Delete the encrypted file after successful decryption
        os.remove(filepath)

        messagebox.showinfo("Succès", f"Fichier déchiffré avec succès!\nSauvegardé comme: {os.path.basename(original_path)}\nFichier chiffré supprimé.")
        
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du déchiffrement: {str(e)}")

def get_user_files():
    """Get all PDF files exported by the current user"""
    jwt_token = get_jwt_token_global()
    if not jwt_token:
        messagebox.showerror("Erreur", "Vous devez être connecté pour accéder à vos fichiers")
        return []
    
    try:
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.get('https://127.0.0.1:5000/api/user/files', headers=headers, verify=False)
        
        if response.status_code != 200:
            messagebox.showerror("Erreur", "Impossible de récupérer vos fichiers")
            return []
        
        data = response.json()
        all_files = []
        
        # Add owned files
        for file in data.get('owned_files', []):
            file['type'] = 'owned'
            all_files.append(file)
        
        # Add shared files
        for file in data.get('shared_files', []):
            file['type'] = 'shared'
            all_files.append(file)
        
        return all_files
        
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la récupération des fichiers: {str(e)}")
        return []

