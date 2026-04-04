from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict


class AccountCreate(BaseModel):
    name: str


class AccountUpdate(BaseModel):
    name: str | None = None
    plan: str | None = None


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    plan: str
    created_at: datetime


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    account_id: UUID
    clerk_user_id: str
    name: str
    email: str
    role: str
    created_at: datetime


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    account_id: UUID
    clerk_user_id: str
    name: str
    email: str
    role: str
    account: AccountResponse
    brand_profile: "BrandProfileSummary | None" = None


class BrandProfileSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    setup_complete: bool


class InviteMemberRequest(BaseModel):
    email: str
    role: str = "viewer"


class ClerkWebhookPayload(BaseModel):
    type: str
    data: dict
