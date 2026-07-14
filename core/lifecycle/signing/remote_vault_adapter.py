"""
core/lifecycle/signing/remote_vault_adapter.py
C15 — Remote Vault Adapter

A GAIASecretVault subclass that loads Ed25519 private keys from:
  1. PEM file paths (passed at registration time), or
  2. Environment variables: GAIA_VAULT_KEY_{KEY_ID_UPPER}
     where KEY_ID_UPPER is key_id.upper().replace('-', '_')

Suitable for CI pipelines and lightweight deployments before
a full KMS (HashiCorp Vault / AWS KMS) is wired.

Production KMS usage::

    class HashiCorpVaultAdapter(GAIASecretVault):
        # Override get_private_key() to call hvac client
        ...
"""

from __future__ import annotations

import os
from typing import Dict, Optional

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import (
        Encoding, PublicFormat, load_pem_private_key,
    )
    _CRYPTO_AVAILABLE = True
except ImportError:
    _CRYPTO_AVAILABLE = False
    Ed25519PrivateKey = object  # type: ignore[assignment,misc]

from .gaia_secret_vault import GAIASecretVault, VaultKeyNotFoundError


class RemoteVaultAdapter(GAIASecretVault):
    """
    ENV / PEM-file backed GAIASecretVault adapter.

    Key resolution order for a given *key_id*:
      1. Explicitly registered PEM bytes (via ``register_pem()``)
      2. PEM file on disk (via ``register_pem_file()``)
      3. Environment variable ``GAIA_VAULT_KEY_{KEY_ID_UPPER}``
         containing a PEM-encoded Ed25519 private key.

    All keys are lazily loaded and cached in-process.
    """

    def __init__(self) -> None:
        if not _CRYPTO_AVAILABLE:
            raise RuntimeError(
                "The 'cryptography' package is required. "
                "Install it with: pip install cryptography"
            )
        self._keys: Dict[str, "Ed25519PrivateKey"]  = {}
        self._pem_bytes: Dict[str, bytes] = {}
        self._pem_files: Dict[str, str]   = {}

    # ------------------------------------------------------------------
    # Registration helpers
    # ------------------------------------------------------------------

    def register_pem(self, key_id: str, pem_bytes: bytes) -> str:
        """
        Register a PEM-encoded Ed25519 private key directly.
        Returns *key_id* for convenience.
        """
        self._pem_bytes[key_id] = pem_bytes
        self._keys.pop(key_id, None)  # invalidate cache
        return key_id

    def register_pem_file(self, key_id: str, path: str) -> str:
        """
        Register a path to a PEM-encoded Ed25519 private key file.
        The file is read lazily on first use.
        Returns *key_id* for convenience.
        """
        self._pem_files[key_id] = path
        self._keys.pop(key_id, None)
        return key_id

    # ------------------------------------------------------------------
    # GAIASecretVault interface
    # ------------------------------------------------------------------

    def _env_var_name(self, key_id: str) -> str:
        return "GAIA_VAULT_KEY_" + key_id.upper().replace("-", "_").replace(".", "_")

    def _load_key(self, key_id: str) -> "Ed25519PrivateKey":
        """Resolve and cache the private key for *key_id*."""
        if key_id in self._keys:
            return self._keys[key_id]

        pem: Optional[bytes] = None

        # 1. Explicitly registered PEM bytes
        if key_id in self._pem_bytes:
            pem = self._pem_bytes[key_id]

        # 2. PEM file on disk
        elif key_id in self._pem_files:
            with open(self._pem_files[key_id], "rb") as fh:
                pem = fh.read()

        # 3. Environment variable
        else:
            env_val = os.environ.get(self._env_var_name(key_id))
            if env_val:
                pem = env_val.encode("utf-8")

        if pem is None:
            raise VaultKeyNotFoundError(
                f"Key '{key_id}' not found in RemoteVaultAdapter. "
                f"Register a PEM, a PEM file path, or set env var "
                f"{self._env_var_name(key_id)}."
            )

        private_key = load_pem_private_key(pem, password=None)
        if not isinstance(private_key, Ed25519PrivateKey):
            raise TypeError(
                f"Key '{key_id}' is not an Ed25519 private key "
                f"(got {type(private_key).__name__})."
            )
        self._keys[key_id] = private_key
        return private_key

    def get_private_key(self, key_id: str) -> "Ed25519PrivateKey":
        return self._load_key(key_id)

    def get_public_key_bytes(self, key_id: str) -> bytes:
        return self._load_key(key_id).public_key().public_bytes(
            encoding=Encoding.Raw,
            format=PublicFormat.Raw,
        )

    def has_key(self, key_id: str) -> bool:
        if key_id in self._keys or key_id in self._pem_bytes or key_id in self._pem_files:
            return True
        return bool(os.environ.get(self._env_var_name(key_id)))
