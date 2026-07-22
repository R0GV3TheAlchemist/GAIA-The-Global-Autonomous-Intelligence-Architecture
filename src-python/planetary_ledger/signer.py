# Copyright (c) 2026 Kyle Alexander Steen (R0GV3 The Alchemist). All Rights Reserved.
# NEXUS Planetary Ledger — Signing backends
# Supported: Ed25519 (cryptography library) and HMAC-SHA256 (stdlib fallback).

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from abc import ABC, abstractmethod
from typing import Any


class BaseSigner(ABC):
    @abstractmethod
    def sign(self, event_dict: dict[str, Any]) -> str:
        """Return base64-encoded signature over canonical event JSON."""

    @abstractmethod
    def verify(self, event_dict: dict[str, Any], signature_b64: str) -> bool:
        """Verify a base64-encoded signature."""

    @property
    @abstractmethod
    def algorithm(self) -> str:
        ...

    @staticmethod
    def _canonical(event_dict: dict[str, Any]) -> bytes:
        """Canonical JSON bytes for signing (signature field zeroed)."""
        d = {k: v for k, v in event_dict.items() if k != "signature"}
        return json.dumps(d, sort_keys=True, ensure_ascii=False).encode()


class HMACSigner(BaseSigner):
    """HMAC-SHA256 signer — stdlib only, no extra dependencies."""

    def __init__(self, secret: bytes | str) -> None:
        self._secret = secret.encode() if isinstance(secret, str) else secret

    @property
    def algorithm(self) -> str:
        return "HMAC-SHA256"

    def sign(self, event_dict: dict[str, Any]) -> str:
        msg = self._canonical(event_dict)
        raw = hmac.new(self._secret, msg, hashlib.sha256).digest()
        return base64.b64encode(raw).decode()

    def verify(self, event_dict: dict[str, Any], signature_b64: str) -> bool:
        expected = self.sign(event_dict)
        return hmac.compare_digest(expected, signature_b64)


class Ed25519Signer(BaseSigner):
    """
    Ed25519 signer using the `cryptography` library.
    Falls back gracefully to HMACSigner if `cryptography` is not installed.
    """

    def __init__(
        self,
        private_key_bytes: bytes | None = None,
        public_key_bytes: bytes | None = None,
        hmac_fallback_secret: bytes | str | None = None,
    ) -> None:
        self._fallback: HMACSigner | None = None
        self._private_key = None
        self._public_key = None

        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import (
                Ed25519PrivateKey,
                Ed25519PublicKey,
            )
            from cryptography.hazmat.primitives.serialization import (
                Encoding,
                NoEncryption,
                PrivateFormat,
                PublicFormat,
            )

            if private_key_bytes:
                self._private_key = Ed25519PrivateKey.from_private_bytes(private_key_bytes)
                self._public_key = self._private_key.public_key()
            elif public_key_bytes:
                self._public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)
            else:
                # Generate ephemeral key
                self._private_key = Ed25519PrivateKey.generate()
                self._public_key = self._private_key.public_key()

        except ImportError:
            secret = hmac_fallback_secret or b"nexus-ledger-fallback-secret"
            self._fallback = HMACSigner(secret)

    @property
    def algorithm(self) -> str:
        return "Ed25519" if self._fallback is None else "HMAC-SHA256"

    def sign(self, event_dict: dict[str, Any]) -> str:
        if self._fallback:
            return self._fallback.sign(event_dict)
        msg = self._canonical(event_dict)
        raw = self._private_key.sign(msg)
        return base64.b64encode(raw).decode()

    def verify(self, event_dict: dict[str, Any], signature_b64: str) -> bool:
        if self._fallback:
            return self._fallback.verify(event_dict, signature_b64)
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        msg = self._canonical(event_dict)
        raw_sig = base64.b64decode(signature_b64)
        try:
            self._public_key.verify(raw_sig, msg)
            return True
        except InvalidSignature:
            return False
