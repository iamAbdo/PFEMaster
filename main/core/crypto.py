import os
from nacl import public, encoding, exceptions as nacl_exceptions
from core import account
from tkinter import messagebox

def encrypt_file(filepath):
    user = account.load_account()
    if not user:
        messagebox.showerror("Error", "No account found.")
        return

    pubkey = public.PublicKey(user['public_key'], encoder=encoding.Base64Encoder)
    box = public.SealedBox(pubkey)

    with open(filepath, "rb") as f:
        data = f.read()

    encrypted = box.encrypt(data)

    base, ext = os.path.splitext(filepath)
    output = f"{base}_Encrypted{ext}.enc"

    with open(output, "wb") as f:
        f.write(encrypted)

    messagebox.showinfo("Encryption Successful", f"Encrypted file saved as:\n{output}")
def decrypt_file(filepath):
    if not filepath.endswith(".enc"):
        messagebox.showerror("Invalid file", "File must end with .enc")
        return

    base = os.path.splitext(filepath)[0]
    if '.' not in base:
        messagebox.showerror("Invalid file", "Expected original file extension before .enc")
        return

    user = account.load_account()
    if not user:
        messagebox.showerror("Error", "No account found.")
        return

    print("Loaded account keys...")
    print("Private Key (Base64):", user['private_key'])

    try:
        privkey = public.PrivateKey(user['private_key'], encoder=encoding.Base64Encoder)
    except Exception as e:
        print("Error decoding private key:", e)
        messagebox.showerror("Error", "Invalid private key.")
        return

    box = public.SealedBox(privkey)

    try:
        with open(filepath, "rb") as f:
            data = f.read()
        print("Encrypted file size:", len(data))
    except Exception as e:
        print("Error reading file:", e)
        messagebox.showerror("Error", "Cannot read selected file.")
        return

    try:
        decrypted = box.decrypt(data)
    except nacl_exceptions.CryptoError as e:
        print("CryptoError:", e)
        messagebox.showerror("Decryption Failed", "Could not decrypt the file.")
        return

    ext = base.split('.')[-1]
    orig = '.'.join(base.split('.')[:-1])
    output = f"{orig}_Decrypted.{ext}"

    with open(output, "wb") as f:
        f.write(decrypted)

    messagebox.showinfo("Decryption Successful", f"Decrypted file saved as:\n{output}")

