import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import argon2
import nacl.bindings as sodium

import os
from nacl.secret import SecretBox
from nacl.utils import random

def generate_keypair(password: str, salt: bytes) -> tuple[bytes, bytes]:
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
    
    # Verify private key is 64 bytes
    if len(private_key) != 64:
        raise ValueError("Invalid private key length. Expected 64 bytes.")
    
    # Convert to X25519 keys
    x25519_private = sodium.crypto_sign_ed25519_sk_to_curve25519(private_key)
    x25519_public = sodium.crypto_sign_ed25519_pk_to_curve25519(public_key)
    
    return (x25519_private, x25519_public)

def encrypt_file(key: bytes, filepath: str):
    box = SecretBox(key)
    with open(filepath, 'rb') as f:
        plaintext = f.read()

    nonce = random(SecretBox.NONCE_SIZE)
    ciphertext = box.encrypt(plaintext, nonce)

    with open(filepath + '.enc', 'wb') as f:
        f.write(ciphertext)

    messagebox.showinfo("Success", "File encrypted successfully.")

def decrypt_file(key: bytes, filepath: str):
    box = SecretBox(key)
    try:
        with open(filepath, 'rb') as f:
            encrypted = f.read()

        # Decrypt the message (nonce is included in the encrypted message)
        plaintext = box.decrypt(encrypted)

        with open(filepath + '.dec', 'wb') as f:
            f.write(plaintext)

        messagebox.showinfo("Success", "File decrypted successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Decryption failed: {e}")


def ask_password_and_generate_keys():
    global private_key, public_key

    password = simpledialog.askstring("Password", "Enter password:", show='*')
    if not password:
        return

    salt = b'static_salt_123456'  # Consider saving/deriving this securely per user or file
    private_key, public_key = generate_keypair(password, salt)

    pub_hex = public_key.hex()
    messagebox.showinfo("Public Key", f"Public Key:\n{pub_hex}")

def choose_action():
    action = simpledialog.askstring("Action", "Type 'encrypt' or 'decrypt':")
    if action not in ['encrypt', 'decrypt']:
        messagebox.showerror("Invalid", "Choose either 'encrypt' or 'decrypt'")
        return

    filepath = filedialog.askopenfilename(title="Select File")
    if not filepath:
        return

    if action == 'encrypt':
        encrypt_file(public_key, filepath)
    else:
        decrypt_file(private_key, filepath)

# --- GUI Setup ---
root = tk.Tk()
root.title("Encrypt/Decrypt App")
root.geometry("300x150")

tk.Button(root, text="Start", command=ask_password_and_generate_keys, width=20).pack(pady=10)
tk.Button(root, text="Encrypt/Decrypt File", command=choose_action, width=20).pack(pady=10)

root.mainloop()