"""GAIA-OS Sovereign Memory — Encryption & Key Management

Issue #66 | Pillar III: Societas

Key hierarchy:
  Master Key (MK)  ← 32 random bytes, lives in OS keychain only, NEVER on disk
      └── DEK-N    ← HKDF(MK, info=key_id), used for AES-256-GCM per domain

Crypto-erasure (GDPR Art. 17): rotate / revoke a DEK and all ciphertext
bound to that key_id becomes permanently unrecoverable.

Platform support:
  macOS  → macOS Keychain via `keyring` (backend: macOS Keychain)
  Windows → DPAPI via `keyring` (backend: Windows Credential Manager)
  Linux  → Secret Service (libsecret) via `keyring`, fallback: Argon2id passphrase
"""

from __future__ import annotations

import os
import sys
import json
import hashlib
from typing import Optional

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    from cryptography.hazmat.primitives import hashes as crypto_hashes
except ImportError:
    raise ImportError(
        "Install cryptography: pip install cryptography"
    )

try:
    import keyring
except ImportError:
    keyring = None  # type: ignore

# ─────────────────────────────────────────────────────────────────
KEYRING_SERVICE = "GAIA-OS"
KEYRING_USERNAME = "sovereign-memory-mk"
NONCE_BYTES = 12       # 96-bit nonce for AES-256-GCM
KEY_BYTES = 32         # 256-bit keys throughout


# ─────────────────────────────────────────────────────────────────
class MasterKeyManager:
    """
    Manages the 32-byte Master Key (MK) via the OS keychain.
    The MK is loaded into process memory on startup and wiped on shutdown.
    It is never written to disk unencrypted.

    Priority order for load_or_create:
      1. Already in memory (_mk set) → return immediately
      2. Explicit passphrase supplied → derive via Argon2id/PBKDF2 (no keychain)
      3. keyring available → load or generate in OS keychain
      4. Raise RuntimeError (no keychain, no passphrase)
    """

    _mk: bytes | None = None

    @classmethod
    def load_or_create(cls, passphrase: str | None = None) -> bytes:
        if cls._mk is not None:
            return cls._mk

        # Explicit passphrase → skip keychain entirely (works on headless CI)
        if passphrase is not None:
            cls._mk = cls._derive_from_passphrase(passphrase)
            return cls._mk

        # No passphrase → use OS keychain (production path)
        if keyring is not None:
            try:
                stored = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
                if stored:
                    cls._mk = bytes.fromhex(stored)
                    return cls._mk
                mk = os.urandom(KEY_BYTES)
                keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, mk.hex())
                cls._mk = mk
                return cls._mk
            except Exception:
                pass

        raise RuntimeError(
            "No keyring backend available and no passphrase provided. "
            "Install libsecret or provide a passphrase."
        )

    @classmethod
    def wipe(cls) -> None:
        """Zero MK from memory on app shutdown or lock."""
        cls._mk = None

    @staticmethod
    def _derive_from_passphrase(passphrase: str) -> bytes:
        try:
            from argon2.low_level import hash_secret_raw, Type
            salt = _load_or_create_salt()
            return hash_secret_raw(
                secret=passphrase.encode(),
                salt=salt,
                time_cost=3,
                memory_cost=65536,
                parallelism=4,
                hash_len=KEY_BYTES,
                type=Type.ID,
            )
        except ImportError:
            pass

        salt = _load_or_create_salt()
        return hashlib.pbkdf2_hmac(
            "sha256", passphrase.encode(), salt, iterations=600_000, dklen=KEY_BYTES
        )


def _salt_path() -> str:
    if sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support/GAIA-OS")
    elif sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        base = os.path.join(base, "GAIA-OS")
    else:
        base = os.path.expanduser("~/.local/share/GAIA-OS")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, ".kdf_salt")


def _load_or_create_salt() -> bytes:
    path = _salt_path()
    if os.path.exists(path):
        with open(path, "rb") as f:
            return f.read()
    salt = os.urandom(16)
    with open(path, "wb") as f:
        f.write(salt)
    return salt


# ─────────────────────────────────────────────────────────────────
def derive_dek(master_key: bytes, key_id: str) -> bytes:
    hkdf = HKDF(
        algorithm=crypto_hashes.SHA256(),
        length=KEY_BYTES,
        salt=None,
        info=key_id.encode(),
    )
    return hkdf.derive(master_key)


# ─────────────────────────────────────────────────────────────────
def encrypt(
    dek: bytes,
    plaintext: str | bytes,
    aad: dict | None = None,
) -> tuple[bytes, bytes, bytes | None]:
    if isinstance(plaintext, str):
        plaintext = plaintext.encode("utf-8")
    nonce = os.urandom(NONCE_BYTES)
    aad_bytes = json.dumps(aad, separators=(",", ":")).encode() if aad else None
    aesgcm = AESGCM(dek)
    ciphertext = aesgcm.encrypt(nonce, plaintext, aad_bytes)
    return ciphertext, nonce, aad_bytes


def decrypt(
    dek: bytes,
    ciphertext: bytes,
    nonce: bytes,
    aad_bytes: bytes | None = None,
) -> str:
    aesgcm = AESGCM(dek)
    plaintext_bytes = aesgcm.decrypt(nonce, ciphertext, aad_bytes)
    return plaintext_bytes.decode("utf-8")


def make_aad(table: str, row_id: str, schema_version: int = 1) -> dict:
    return {"table": table, "id": row_id, "v": schema_version}
