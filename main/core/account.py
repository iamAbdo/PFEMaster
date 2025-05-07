import os
import json
import hashlib
from pathlib import Path
from argon2 import PasswordHasher
from nacl import signing, encoding

from nacl.public import PrivateKey
from nacl.encoding import Base64Encoder
from argon2.low_level import hash_secret_raw, Type

APP_NAME = "sincus"
ACCOUNT_FILE = "account.json"
FIXED_SALT = b"myapp-fixed-salt"

# windows or linux
def get_app_data_dir():
    if os.name == 'nt':
        return Path(os.getenv('APPDATA')) / APP_NAME
    else:
        return Path.home() / ".config" / APP_NAME

def get_account_path():
    app_data_dir = get_app_data_dir()
    app_data_dir.mkdir(parents=True, exist_ok=True)
    return app_data_dir / ACCOUNT_FILE

def username_from_email(email):
    return email.split("@")[0]

def derive_keys_from_password(password):
    salt = b"sincus-fixed-salt"
    seed = hash_secret_raw(
        secret=password.encode(),
        salt=salt,
        time_cost=3,
        memory_cost=65536,
        parallelism=4,
        hash_len=32,
        type=Type.ID
    )
    priv = PrivateKey(seed)
    pub = priv.public_key
    return priv.encode(encoder=Base64Encoder).decode(), pub.encode(encoder=Base64Encoder).decode()
    
def load_account():
    path = get_account_path()
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return None

def save_account(email, password):
    username = username_from_email(email)
    priv, pub = derive_keys_from_password(password)
    data = {
        "email": email,
        "username": username,
        "private_key": priv,
        "public_key": pub
    }
    with open(get_account_path(), "w") as f:
        json.dump(data, f, indent=4)
    return data


def delete_account():
    path = get_account_path()
    if os.path.exists(path):
        os.remove(path)