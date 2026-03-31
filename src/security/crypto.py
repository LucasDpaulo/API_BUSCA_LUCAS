"""Criptografia simétrica para proteger tokens e senhas no banco."""

import os
from pathlib import Path

from cryptography.fernet import Fernet

_KEY_FILE = Path(__file__).resolve().parent.parent.parent / ".secret.key"


def _load_or_create_key() -> bytes:
    """Carrega a chave do arquivo ou gera uma nova na primeira execução."""
    if _KEY_FILE.exists():
        return _KEY_FILE.read_bytes()

    key = Fernet.generate_key()
    _KEY_FILE.write_bytes(key)
    # Permissão restrita: só o dono lê/escreve
    os.chmod(_KEY_FILE, 0o600)
    return key


_fernet = Fernet(_load_or_create_key())


def encrypt(value: str) -> str:
    """Cifra uma string e retorna o texto cifrado em base64."""
    return _fernet.encrypt(value.encode()).decode()


def decrypt(value: str) -> str:
    """Decifra um texto cifrado e retorna a string original."""
    return _fernet.decrypt(value.encode()).decode()
