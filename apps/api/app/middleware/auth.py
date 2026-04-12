from typing import Annotated, Optional
from uuid import UUID
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import httpx

from app.config import get_settings
from app.database import get_db
from app.models.accounts import Account, User, UserRole

settings = get_settings()
security = HTTPBearer(auto_error=False)  # Don't reject missing token — dev bypass handles it

DEV_USER_ID  = UUID("00000000-0000-0000-0000-000000000001")
DEV_ACCOUNT_ID = UUID("00000000-0000-0000-0000-000000000002")

_jwks_cache: dict | None = None


async def _get_jwks() -> dict:
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache
    async with httpx.AsyncClient() as client:
        resp = await client.get(settings.CLERK_JWKS_URL)
        resp.raise_for_status()
        _jwks_cache = resp.json()
        return _jwks_cache


async def _verify_clerk_token(token: str) -> dict:
    try:
        jwks = await _get_jwks()
        header = jwt.get_unverified_header(token)
        key = None
        for k in jwks.get("keys", []):
            if k["kid"] == header.get("kid"):
                key = k
                break
        if key is None:
            raise HTTPException(status_code=401, detail="Invalid token signing key")
        payload = jwt.decode(token, key, algorithms=["RS256"], options={"verify_aud": False})
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")


from types import SimpleNamespace

_DEV_USER_STUB: SimpleNamespace | None = None


def _make_dev_user_stub() -> SimpleNamespace:
    """
    Create an in-memory dev user stub so routes work without a DB.
    Uses SimpleNamespace so SQLAlchemy instrumentation is bypassed entirely.
    Routes that need real DB rows will handle failures themselves.
    """
    account = SimpleNamespace(
        id=DEV_ACCOUNT_ID,
        name="Dev Account",
        plan="growth",
    )
    user = SimpleNamespace(
        id=DEV_USER_ID,
        account_id=DEV_ACCOUNT_ID,
        clerk_user_id="dev_user",
        name="Dev User",
        email="dev@competeiq.local",
        role=UserRole.owner,
        account=account,
    )
    return user


async def _get_or_create_dev_user(db: AsyncSession) -> User:
    """Return the persistent dev user — falls back to in-memory stub if DB is down."""
    global _DEV_USER_STUB
    try:
        stmt = (
            select(User)
            .options(selectinload(User.account))
            .where(User.id == DEV_USER_ID)
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            _DEV_USER_STUB = None  # clear stale stub
            return user

        # Create dev account
        account = Account(id=DEV_ACCOUNT_ID, name="Dev Account")
        db.add(account)
        await db.flush()

        # Create dev user
        user = User(
            id=DEV_USER_ID,
            account_id=DEV_ACCOUNT_ID,
            clerk_user_id="dev_user",
            name="Dev User",
            email="dev@competeiq.local",
            role=UserRole.owner,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)

        # Reload with relationship
        stmt = (
            select(User)
            .options(selectinload(User.account))
            .where(User.id == DEV_USER_ID)
        )
        result = await db.execute(stmt)
        return result.scalar_one()

    except Exception:
        # DB unavailable — return in-memory stub so routes can still function
        if _DEV_USER_STUB is None:
            _DEV_USER_STUB = _make_dev_user_stub()
        return _DEV_USER_STUB


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    # ── Dev bypass ──────────────────────────────────────────────────────────
    if settings.ENVIRONMENT == "development" and request.headers.get("X-Dev-Token") == "dev":
        # Return in-memory stub immediately — no DB required
        # This lets the API work without PostgreSQL in local dev
        global _DEV_USER_STUB
        if _DEV_USER_STUB is None:
            _DEV_USER_STUB = _make_dev_user_stub()
        return _DEV_USER_STUB

    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = await _verify_clerk_token(credentials.credentials)
    clerk_user_id = payload.get("sub")
    if not clerk_user_id:
        raise HTTPException(status_code=401, detail="Invalid token: no subject")

    stmt = (
        select(User)
        .options(selectinload(User.account))
        .where(User.clerk_user_id == clerk_user_id)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found. Complete account setup first.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(*roles: UserRole):
    async def _check_role(current_user: CurrentUser) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role: {', '.join(r.value for r in roles)}",
            )
        return current_user
    return _check_role


async def get_account_id(current_user: CurrentUser) -> UUID:
    return current_user.account_id


AccountId = Annotated[UUID, Depends(get_account_id)]
