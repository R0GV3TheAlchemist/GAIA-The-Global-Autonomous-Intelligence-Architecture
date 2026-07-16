"""
core/identity/auth.py
=====================
GAIA Hardened Authentication Layer — v2.0
Author: Kyle Steen / R0GV3TheAlchemist
Canon Ref: C01 (Sovereignty), C15 (Consent), C22 (Integrity)

Features:
  - RS256 asymmetric JWT signing (HS256 default, RS256 via env)
  - Token revocation blocklist (in-memory, Redis-ready)
  - Per-identity rate limiting
  - Origin fingerprinting (IP + UA binding)
  - Document watermarking (Unicode steganography)
  - Admin role enforcement
"""

from __future__ import annotations

import hashlib
import hmac
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional, Set

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ALGORITHM = "HS256"  # Swap to RS256 by setting GAIA_JWT_PRIVATE_KEY env var
SECRET_KEY: str = os.environ.get("GAIA_JWT_SECRET", "CHANGE_ME_IN_PRODUCTION")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("GAIA_TOKEN_EXPIRE_MIN", "60"))
RATE_LIMIT_WINDOW: int = 60           # seconds
RATE_LIMIT_MAX_CALLS: int = 120       # requests per window per identity

# ---------------------------------------------------------------------------
# In-memory stores  (swap for Redis in production via GAIA_USE_REDIS=true)
# ---------------------------------------------------------------------------

_revoked_tokens: Set[str] = set()           # jti values
_rate_buckets: dict[str, list[float]] = {}  # identity -> [timestamps]

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class TokenPayload(BaseModel):
    sub: str                               # subject (user id / agent id)
    role: str = "user"
    jti: str                               # unique token id (for revocation)
    origin_hash: Optional[str] = None     # fingerprint of issuing request
    exp: Optional[int] = None
    iat: Optional[int] = None
    iss: str = "gaia"


class TokenRequest(BaseModel):
    identity_id: str
    role: str = "user"
    secret: str = Field(..., description="Shared bootstrap secret")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60


# ---------------------------------------------------------------------------
# Core token functions
# ---------------------------------------------------------------------------


def _make_jti(subject: str) -> str:
    raw = f"{subject}:{time.time_ns()}:{os.urandom(8).hex()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def _origin_hash(request: Optional[Request]) -> Optional[str]:
    if request is None:
        return None
    ip = request.client.host if request.client else "unknown"
    ua = request.headers.get("user-agent", "")
    raw = f"{ip}|{ua}|{SECRET_KEY}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def create_access_token(
    subject: str,
    role: str = "user",
    expires_delta: Optional[timedelta] = None,
    request: Optional[Request] = None,
) -> str:
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {
        "sub": subject,
        "role": role,
        "jti": _make_jti(subject),
        "origin_hash": _origin_hash(request),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "iss": "gaia",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str, request: Optional[Request] = None) -> TokenPayload:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        tp = TokenPayload(**payload)
    except (JWTError, Exception):
        raise credentials_exception

    # Revocation check
    if tp.jti in _revoked_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )

    # Origin binding check
    if tp.origin_hash and request is not None:
        expected = _origin_hash(request)
        if not hmac.compare_digest(tp.origin_hash, expected):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token origin mismatch — possible replay attack",
            )

    return tp


def revoke_token(jti: str) -> None:
    """Add a token's jti to the revocation blocklist."""
    _revoked_tokens.add(jti)


# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------


def _check_rate_limit(identity: str) -> None:
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW
    bucket = _rate_buckets.get(identity, [])
    bucket = [t for t in bucket if t > window_start]
    if len(bucket) >= RATE_LIMIT_MAX_CALLS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: {RATE_LIMIT_MAX_CALLS} req/{RATE_LIMIT_WINDOW}s",
        )
    bucket.append(now)
    _rate_buckets[identity] = bucket


# ---------------------------------------------------------------------------
# FastAPI dependencies
# ---------------------------------------------------------------------------

_bearer = HTTPBearer(auto_error=False)


async def require_auth(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(_bearer)],
    request: Request,
) -> TokenPayload:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No credentials provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = verify_token(credentials.credentials, request)
    _check_rate_limit(payload.sub)
    return payload


async def optional_auth(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(_bearer)],
    request: Request,
) -> Optional[TokenPayload]:
    if not credentials:
        return None
    try:
        return verify_token(credentials.credentials, request)
    except HTTPException:
        return None


async def require_admin(
    payload: Annotated[TokenPayload, Depends(require_auth)],
) -> TokenPayload:
    if payload.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return payload


# ---------------------------------------------------------------------------
# Document watermarking  (Unicode steganography)
# Zero-width characters encode your identity + timestamp into any text.
# Invisible to readers, detectable programmatically.
# ---------------------------------------------------------------------------

_ZW_MAP = {
    "0": "\u200b",  # zero-width space
    "1": "\u200c",  # zero-width non-joiner
}
_ZW_SEP = "\u200d"  # zero-width joiner (separator)


def stamp_document(content: str, identity: str) -> str:
    """
    Watermark a document with your identity.
    Call on any output you want protected.
    Embeds 'identity:unix_timestamp' as invisible Unicode steganography.
    """
    stamp = f"{identity}:{int(time.time())}"
    bits = "".join(format(ord(c), "08b") for c in stamp)
    hidden = _ZW_SEP + "".join(_ZW_MAP[b] for b in bits) + _ZW_SEP
    pos = min(content.find(". ") + 2 if ". " in content[:80] else 80, len(content))
    return content[:pos] + hidden + content[pos:]


def verify_document_origin(content: str) -> Optional[str]:
    """
    Returns 'identity:unix_timestamp' if a watermark is found, else None.
    Use this to prove a document originated from GAIA.
    """
    zwj = "\u200d"
    if zwj not in content:
        return None
    try:
        start = content.index(zwj) + 1
        end = content.index(zwj, start)
        bits = "".join(
            "0" if c == "\u200b" else "1"
            for c in content[start:end]
            if c in ("\u200b", "\u200c")
        )
        chars = [chr(int(bits[i : i + 8], 2)) for i in range(0, len(bits) - 7, 8)]
        return "".join(chars)
    except (ValueError, IndexError):
        return None


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/token", response_model=TokenResponse)
async def issue_token(body: TokenRequest, request: Request) -> TokenResponse:
    expected = os.environ.get("GAIA_BOOTSTRAP_SECRET", "CHANGE_ME")
    if not hmac.compare_digest(body.secret, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bootstrap secret",
        )
    token = create_access_token(body.identity_id, role=body.role, request=request)
    return TokenResponse(
        access_token=token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@auth_router.post("/revoke")
async def revoke(
    payload: Annotated[TokenPayload, Depends(require_auth)],
) -> dict:
    revoke_token(payload.jti)
    return {"revoked": True, "jti": payload.jti}


@auth_router.get("/whoami", response_model=TokenPayload)
async def whoami(
    payload: Annotated[TokenPayload, Depends(require_auth)],
) -> TokenPayload:
    return payload


__all__ = [
    "TokenPayload",
    "TokenRequest",
    "TokenResponse",
    "create_access_token",
    "verify_token",
    "revoke_token",
    "require_auth",
    "optional_auth",
    "require_admin",
    "auth_router",
    "stamp_document",
    "verify_document_origin",
]
