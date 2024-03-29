import subprocess
from datetime import datetime
from pathlib import Path
from typing import Union, Optional

from cryptography.fernet import Fernet
from hashlib import sha256
import base64

from file_share.definitions.dataclasses import DecryptedFile
from file_share.definitions import hash_iterations


def _get_key(token: bytes, seed: bytes) -> bytes:
    key_gen = sha256()
    key_gen.update(token)
    key_gen.update(seed)
    return base64.b64encode(key_gen.digest()[-32:])


def encrypt(data: bytes, token: bytes, seed: bytes) -> bytes:
    encryption_factory = Fernet(_get_key(token, seed))
    return encryption_factory.encrypt(data)


def decrypt(data: bytes, token: bytes, seed: bytes) -> bytes:
    decryption_factory = Fernet(_get_key(token, seed))
    return decryption_factory.decrypt(data)


def load_file(
    path: Union[str, Path], send_to: str, override_address: Optional[str] = None
) -> DecryptedFile:
    """
    Load file from filesystem and prepare it for sending by
    wrapping it in DecryptedFile object.

    Args:
        path (Union[str, Path]): path to file that needs to be loaded
        send_to (str): peer to receive the file
        override_address (str): IP address if we want to specify it explicitly
            and not just count on the DB
    """
    if isinstance(path, str):
        path = Path(path)
    with open(path, "rb") as infile:
        data = infile.read()
    return DecryptedFile(
        username=send_to,
        incoming=False,
        timestamp=datetime.now(),
        filename=path.name,
        data=data,
        override_address=override_address,
    )


def compute_token(password: str, seed: bytes) -> bytes:
    token_factory = sha256()
    token_factory.update(seed)
    token_factory.update(password.encode())
    data = token_factory.digest()
    for _ in range(hash_iterations):
        token_factory.update(data)
        data = token_factory.digest()
    return data


def get_token_hash(token: bytes) -> bytes:
    hash_factory = sha256()
    hash_factory.update(token)
    return hash_factory.digest()


def create_cert(name: str, location: Path):
    """Creates a certificate file."""
    Path(location).mkdir(exist_ok=True)
    subprocess.run(
        [
            "openssl",
            "req",
            "-x509",
            "-newkey",
            "rsa:4096",
            "-keyout",
            f"{location}/rsa.key",
            "-out",
            f"{location}/rsa.crt",
            "-days",
            "3650",
            "-nodes",
            "-subj",
            f"/C=CZ/ST=JMK/L=Brno/O=VUT/OU=FEKT/CN={name}",
        ]
    )
