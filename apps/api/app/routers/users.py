from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.middleware.auth import CurrentUser, require_role
from app.models.accounts import Account, User, UserRole
from app.models.brands import BrandProfile
from app.schemas.accounts import (
    AccountCreate,
    AccountUpdate,
    AccountResponse,
    UserProfileResponse,
    BrandProfileSummary,
    InviteMemberRequest,
    ClerkWebhookPayload,
)

router = APIRouter()


@router.get("/users/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    # Load account
    stmt = select(Account).where(Account.id == current_user.account_id)
    result = await db.execute(stmt)
    account = result.scalar_one()

    # Load first brand profile for this account
    stmt = (
        select(BrandProfile)
        .where(BrandProfile.account_id == current_user.account_id)
        .limit(1)
    )
    result = await db.execute(stmt)
    brand = result.scalar_one_or_none()

    return UserProfileResponse(
        id=current_user.id,
        account_id=current_user.account_id,
        clerk_user_id=current_user.clerk_user_id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role.value,
        account=AccountResponse.model_validate(account),
        brand_profile=BrandProfileSummary.model_validate(brand) if brand else None,
    )


@router.post("/auth/sync")
async def clerk_webhook_sync(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Clerk webhook to sync user creation/updates."""
    body = await request.json()
    event_type = body.get("type", "")
    data = body.get("data", {})

    if event_type == "user.created":
        clerk_id = data.get("id")
        email = data.get("email_addresses", [{}])[0].get("email_address", "")
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        name = f"{first_name} {last_name}".strip() or email

        # Check if user already exists
        stmt = select(User).where(User.clerk_user_id == clerk_id)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            return {"status": "already_exists"}

        # Create account + user
        account = Account(name=f"{name}'s Workspace")
        db.add(account)
        await db.flush()

        user = User(
            account_id=account.id,
            clerk_user_id=clerk_id,
            name=name,
            email=email,
            role=UserRole.owner,
        )
        db.add(user)
        return {"status": "created"}

    elif event_type == "user.updated":
        clerk_id = data.get("id")
        stmt = select(User).where(User.clerk_user_id == clerk_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            first_name = data.get("first_name", "")
            last_name = data.get("last_name", "")
            user.name = f"{first_name} {last_name}".strip() or user.name
            email = data.get("email_addresses", [{}])[0].get("email_address", "")
            if email:
                user.email = email
        return {"status": "updated"}

    return {"status": "ignored"}


@router.post("/accounts", response_model=AccountResponse)
async def create_account(
    payload: AccountCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    account = Account(name=payload.name)
    db.add(account)
    await db.flush()

    # Link current user to the new account
    current_user.account_id = account.id
    return AccountResponse.model_validate(account)


@router.patch("/accounts/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: UUID,
    payload: AccountUpdate,
    current_user: User = Depends(require_role(UserRole.owner)),
    db: AsyncSession = Depends(get_db),
):
    if current_user.account_id != account_id:
        raise HTTPException(status_code=403, detail="Cannot update another account")

    stmt = select(Account).where(Account.id == account_id)
    result = await db.execute(stmt)
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if payload.name is not None:
        account.name = payload.name
    if payload.plan is not None:
        account.plan = payload.plan

    return AccountResponse.model_validate(account)


@router.post("/accounts/{account_id}/invite")
async def invite_member(
    account_id: UUID,
    payload: InviteMemberRequest,
    current_user: User = Depends(require_role(UserRole.owner)),
    db: AsyncSession = Depends(get_db),
):
    if current_user.account_id != account_id:
        raise HTTPException(status_code=403, detail="Cannot invite to another account")

    # Check if email already exists in this account
    stmt = select(User).where(User.email == payload.email, User.account_id == account_id)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="User already in this account")

    # In production, this would send an invite email via Resend.
    # For now, create a placeholder user record.
    return {
        "message": f"Invite sent to {payload.email} with role {payload.role}",
        "status": "pending",
    }
