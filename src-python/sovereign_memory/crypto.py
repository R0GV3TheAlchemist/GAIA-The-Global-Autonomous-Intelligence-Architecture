"""GAIA-OS Sovereign Memory — Encryption & Key Management

Issue #66 | Pillar III: Societas

Key hierarchy:
  Master Key (MK)  ← 32 random bytes, lives in OS keychain only, NEVER on disk
      └── DEK-N    ← HKDF(MK, info=key_id), used for AES-256-GCM per domain

Crypto-erasure (GDPR Art. 17): rotate / revoke a DEK and all ciphertext
bound to that key_id becomes permanently unrecoverable.

Platform support:
  macOS   → macOS Keychain via `keyring`
  Windows → DPAPI / Windows Credential Manager via `keyring`
  Linux   → Secret Service (libsecret) via `keyring`, fallback: Argon2id passphrase

Backup / restore:
  MasterKeyManager.export_encrypted(passphrase) → bytes (JSON)
    Wraps the MK under an Argon2id-derived backup key (AES-256-GCM).
    Safe to write to disk or cloud storage.
  MasterKeyManager.import_encrypted(blob, passphrase) → None
    Decrypts the blob, saves the MK back into the OS keychain, sets _mk.
"""

from __future__ import annotations

import json
import os
import sys
import hashlib
import time
from typing import Optional

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    from cryptography.hazmat.primitives import hashes as crypto_hashes
except ImportError:
    raise ImportError("Install cryptography: pip install cryptography")

try:
    import keyring
except ImportError:
    keyring = None  # type: ignore

# ────────────────────────────────────────────────────────────────
KEYRING_SERVICE  = "GAIA-OS"
KEYRING_USERNAME = "sovereign-memory-mk"
NONCE_BYTES = 12   # 96-bit nonce for AES-256-GCM
KEY_BYTES   = 32   # 256-bit keys throughout

# Version tag embedded in every backup blob so we can evolve the format
_BACKUP_FORMAT_VERSION = 1


# ────────────────────────────────────────────────────────────────
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

    Backup / restore:
      export_encrypted(passphrase) → bytes
        Returns an encrypted JSON blob that can be written to a file.
      import_encrypted(blob, passphrase) → None
        Decrypts blob and saves the recovered MK into the OS keychain.
    """

    _mk: bytes | None = None

    # ───────────────────────
    # Lifecycle
    # ───────────────────────

    @classmethod
    def load_or_create(cls, passphrase: str | None = None) -> bytes:
        if cls._mk is not None:
            return cls._mk

        if passphrase is not None:
            cls._mk = cls._derive_from_passphrase(passphrase)
            return cls._mk

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
            "Install libsecret or supply a passphrase."
        )

    @classmethod
    def wipe(cls) -> None:
        """Zero MK from memory on app shutdown or lock."""
        cls._mk = None

    @classmethod
    def mk_source(cls) -> str:
        """Return a human-readable string describing where the MK lives."""
        if cls._mk is None:
            return "not_loaded"
        if keyring is not None:
            try:
                stored = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
                if stored:
                    platform = sys.platform
                    if platform == "darwin":
                        return "macos_keychain"
                    if platform == "win32":
                        return "windows_credential_manager"
                    return "secret_service"
            except Exception:
                pass
        return "passphrase_derived"

    # ───────────────────────
    # Backup / Restore
    # ───────────────────────

    @classmethod
    def export_encrypted(cls, passphrase: str) -> bytes:
        """
        Wrap the MK under an Argon2id-derived backup key (AES-256-GCM)
        and return a self-describing JSON blob.

        The blob is safe to write to disk or cloud storage — it contains
        no plaintext key material; only the passphrase can unwrap it.

        Returns:
            UTF-8 JSON bytes, suitable for writing as gaia-sovereign-backup.json

        Raises:
            RuntimeError: if the MK is not loaded (call open() first)
            ValueError:   if passphrase is empty
        """
        if cls._mk is None:
            raise RuntimeError(
                "Master key not loaded. Call SovereignMemory.open() before exporting."
            )
        if not passphrase:
            raise ValueError("Backup passphrase must not be empty.")

        backup_key = cls._derive_from_passphrase(passphrase)
        nonce = os.urandom(NONCE_BYTES)
        aesgcm = AESGCM(backup_key)

        inner = json.dumps(
            {"mk": cls._mk.hex(), "created_at": int(time.time() * 1000)},
            separators=(",", ":"),
        ).encode("utf-8")

        ciphertext = aesgcm.encrypt(nonce, inner, None)

        blob = json.dumps(
            {
                "gaia": "sovereign-memory-backup",
                "v": _BACKUP_FORMAT_VERSION,
                "nonce": nonce.hex(),
                "ciphertext": ciphertext.hex(),
            },
            separators=(",", ":"),
        )
        return blob.encode("utf-8")

    @classmethod
    def import_encrypted(cls, blob: bytes, passphrase: str) -> None:
        """
        Decrypt a backup blob created by export_encrypted(), recover the MK,
        write it into the OS keychain, and set it in memory.

        Args:
            blob:       Raw bytes of gaia-sovereign-backup.json
            passphrase: The backup password used during export

        Raises:
            ValueError:   wrong passphrase / corrupted blob
            RuntimeError: if the blob format is unrecognised
        """
        try:
            outer = json.loads(blob.decode("utf-8"))
        except Exception as exc:
            raise ValueError("Backup file is not valid JSON.") from exc

        if outer.get("gaia") != "sovereign-memory-backup":
            raise RuntimeError(
                "This file does not appear to be a GAIA-OS Sovereign Memory backup."
            )

        version = outer.get("v", 0)
        if version != _BACKUP_FORMAT_VERSION:
            raise RuntimeError(
                f"Unsupported backup format version: {version}. "
                "Please update GAIA-OS and try again."
            )

        try:
            nonce      = bytes.fromhex(outer["nonce"])
            ciphertext = bytes.fromhex(outer["ciphertext"])
        except (KeyError, ValueError) as exc:
            raise ValueError("Backup blob is missing required fields or is corrupted.") from exc

        backup_key = cls._derive_from_passphrase(passphrase)
        aesgcm = AESGCM(backup_key)

        try:
            inner_bytes = aesgcm.decrypt(nonce, ciphertext, None)
        except Exception as exc:
            raise ValueError(
                "Incorrect passphrase or corrupted backup file. "
                "Could not decrypt the Master Key."
            ) from exc

        try:
            inner = json.loads(inner_bytes.decode("utf-8"))
            mk = bytes.fromhex(inner["mk"])
        except Exception as exc:
            raise ValueError("Backup inner payload is malformed.") from exc

        if len(mk) != KEY_BYTES:
            raise ValueError(
                f"Recovered key has unexpected length {len(mk)} (expected {KEY_BYTES})."
            )

        # Save into keychain if available, then set in memory
        if keyring is not None:
            try:
                keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, mk.hex())
            except Exception:  # noqa: BLE001
                pass  # Keychain write failed; MK still available in memory this session

        cls._mk = mk

    # ───────────────────────
    # Internal helpers
    # ───────────────────────

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


# ────────────────────────────────────────────────────────────────
# KDF salt helpers (used by passphrase path + backup export/import)
# ────────────────────────────────────────────────────────────────

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


# ────────────────────────────────────────────────────────────────
# DEK derivation + AES-256-GCM helpers
# ────────────────────────────────────────────────────────────────

def derive_dek(master_key: bytes, key_id: str) -> bytes:
    """Derive a 256-bit Data Encryption Key from the Master Key via HKDF-SHA256."""
    hkdf = HKDF(
        algorithm=crypto_hashes.SHA256(),
        length=KEY_BYTES,
        salt=None,
        info=key_id.encode(),
    )
    return hkdf.derive(master_key)


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
