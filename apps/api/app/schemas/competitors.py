from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.schemas.brands import SocialProfilesSchema


class CompetitorCreate(BaseModel):
    name: str
    website: str | None = None
    tier: str = "direct"
    social_profiles: SocialProfilesSchema | None = None
    ad_library_url: str | None = None


class CompetitorUpdate(BaseModel):
    name: str | None = None
    website: str | None = None
    tier: str | None = None
    social_profiles: SocialProfilesSchema | None = None
    ad_library_url: str | None = None
    active: bool | None = None


class CompetitorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    brand_profile_id: UUID
    name: str
    website: str | None
    tier: str
    social_profiles: dict | None
    ad_library_url: str | None
    ai_discovered: bool
    active: bool
    created_at: datetime


class CompetitorDiscoveryResult(BaseModel):
    name: str
    website: str | None = None
    suggested_tier: str
    reason: str
    relevance_score: int
    social_profiles: SocialProfilesSchema | None = None
