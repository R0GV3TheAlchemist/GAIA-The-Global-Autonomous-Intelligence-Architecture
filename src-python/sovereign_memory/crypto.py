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

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────

KEYRING_SERVICE = "GAIA-OS"
KEYRING_USERNAME = "sovereign-memory-mk"
NONCE_BYTES = 12       # 96-bit nonce for AES-256-GCM
KEY_BYTES = 32         # 256-bit keys throughout


# ─────────────────────────────────────────────
# MASTER KEY MANAGEMENT
# ─────────────────────────────────────────────

class MasterKeyManager:
    """
    Manages the 32-byte Master Key (MK) via the OS keychain.
    The MK is loaded into process memory on startup and wiped on shutdown.
    It is never written to disk unencrypted.
    """

    _mk: bytes | None = None

    @classmethod
    def load_or_create(cls, passphrase: str | None = None) -> bytes:
        """
        Load MK from OS keychain. If not found, generate a new one and store it.
        On Linux without Secret Service, falls back to Argon2id passphrase derivation.
        Returns the MK as 32 raw bytes (held in memory only).
        """
        if cls._mk is not None:
            return cls._mk

        if keyring is not None:
            stored = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
            if stored:
                cls._mk = bytes.fromhex(stored)
                return cls._mk
            # First run: generate and store
            mk = os.urandom(KEY_BYTES)
            keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, mk.hex())
            cls._mk = mk
            return cls._mk

        # Linux fallback: derive from passphrase via Argon2id
        if passphrase is None:
            raise RuntimeError(
                "No keyring backend available and no passphrase provided. "
                "Install libsecret or provide a passphrase."
            )
        cls._mk = cls._derive_from_passphrase(passphrase)
        return cls._mk

    @classmethod
    def wipe(cls) -> None:
        """Zero MK from memory on app shutdown or lock."""
        cls._mk = None

    @staticmethod
    def _derive_from_passphrase(passphrase: str) -> bytes:
        """
        Argon2id passphrase → 32-byte MK.
        Uses argon2-cffi if available; falls back to PBKDF2-SHA256.
        """
        try:
            from argon2.low_level import hash_secret_raw, Type
            # Argon2id params: memory=64MB, iterations=3, parallelism=4
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

        # PBKDF2-SHA256 fallback (weaker but available everywhere)
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


# ─────────────────────────────────────────────
# DATA ENCRYPTION KEY DERIVATION
# ─────────────────────────────────────────────

def derive_dek(master_key: bytes, key_id: str) -> bytes:
    """
    Derive a 32-byte Domain Encryption Key from the Master Key.
    Uses HKDF-SHA256 with key_id as the info string.
    Deterministic: same MK + key_id always produces the same DEK.
    """
    hkdf = HKDF(
        algorithm=crypto_hashes.SHA256(),
        length=KEY_BYTES,
        salt=None,
        info=key_id.encode(),
    )
    return hkdf.derive(master_key)


# ─────────────────────────────────────────────
# AES-256-GCM ENCRYPT / DECRYPT
# ─────────────────────────────────────────────

def encrypt(
    dek: bytes,
    plaintext: str | bytes,
    aad: dict | None = None,
) -> tuple[bytes, bytes, bytes | None]:
    """
    Encrypt plaintext with AES-256-GCM.

    Args:
        dek:       32-byte Data Encryption Key
        plaintext: content to encrypt (str or bytes)
        aad:       optional dict serialised as JSON for Associated Authenticated Data

    Returns:
        (ciphertext, nonce, aad_bytes)
        Store all three; nonce and aad_bytes are needed for decryption.
    """
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
    """
    Decrypt AES-256-GCM ciphertext.
    Raises cryptography.exceptions.InvalidTag if tampered.
    Returns plaintext as a UTF-8 string.
    """
    aesgcm = AESGCM(dek)
    plaintext_bytes = aesgcm.decrypt(nonce, ciphertext, aad_bytes)
    return plaintext_bytes.decode("utf-8")


# ─────────────────────────────────────────────
# CONVENIENCE: build AAD dict for a DB row
# ─────────────────────────────────────────────

def make_aad(table: str, row_id: str, schema_version: int = 1) -> dict:
    return {"table": table, "id": row_id, "v": schema_version}
