"""JWT bearer authentication and role-based access control.

Four roles, each scoped to a jurisdiction. A district officer holding a token for one
agency cannot read another agency's case files — enforced server-side, and tested on the
failure path, not only the happy path.

**Prototype honesty:** tokens are seeded from a signing key in config, not issued by an
identity provider, and there is no user registry or password storage. Production would put
a real IdP in front of exactly this dependency; nothing else would change.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from mplads import config

ALGORITHM = "HS256"
_bearer = HTTPBearer(auto_error=False)

#: role -> the field its scope narrows, and whether it may read everything.
ROLE_SCOPE: dict[str, str | None] = {
    "ministry": None,          # unrestricted
    "auditor": None,           # unrestricted (CAG / MoSPI audit)
    "state": "state",
    "district": "implementing_agency",
    "mp": "constituency",
}


@dataclass
class Principal:
    subject: str
    role: str
    scope: str | None

    @property
    def unrestricted(self) -> bool:
        return ROLE_SCOPE.get(self.role) is None

    def may_read(self, row: dict) -> bool:
        """Can this principal see this work?"""
        if self.unrestricted:
            return True
        field = ROLE_SCOPE.get(self.role)
        if field is None or self.scope is None:
            return False
        return row.get(field) == self.scope


def issue_token(subject: str, role: str, scope: str | None = None, hours: int = 12) -> str:
    if role not in ROLE_SCOPE:
        raise ValueError(f"unknown role: {role}")
    now = dt.datetime.now(dt.timezone.utc)
    payload = {
        "sub": subject,
        "role": role,
        "scope": scope,
        "iat": now,
        "exp": now + dt.timedelta(hours=hours),
    }
    return jwt.encode(payload, config.JWT_SECRET, algorithm=ALGORITHM)


def decode_token(token: str) -> Principal:
    try:
        claims = jwt.decode(token, config.JWT_SECRET, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid token")
    return Principal(claims["sub"], claims["role"], claims.get("scope"))


def current_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> Principal:
    """Authenticated principal, or the open-data reader when auth is disabled."""
    if not config.REQUIRE_AUTH:
        return Principal("anonymous", "ministry", None)
    if credentials is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return decode_token(credentials.credentials)


def require_scope(principal: Principal, row: dict, resource: str) -> None:
    """403 if the principal is outside its jurisdiction. The tested failure path."""
    if not principal.may_read(row):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            f"{principal.role} '{principal.scope}' is not authorised to read {resource}",
        )


def seed_demo_tokens() -> dict[str, str]:
    """Tokens for the demo. Printed by `mplads tokens`; never a production mechanism."""
    return {
        "ministry": issue_token("demo-ministry", "ministry"),
        "auditor": issue_token("demo-auditor", "auditor"),
        "state_bihar": issue_token("demo-state-bihar", "state", "Bihar"),
        "mp_saran": issue_token("demo-mp-saran", "mp", "SARAN"),
    }
