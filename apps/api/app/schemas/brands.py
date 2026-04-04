from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, HttpUrl


class SocialProfilesSchema(BaseModel):
    facebook_url: str | None = None
    instagram_handle: str | None = None
    linkedin_url: str | None = None
    youtube_url: str | None = None


class BrandPersonaSchema(BaseModel):
    brand_voice: str
    core_audience: str
    value_propositions: list[str]
    market_positioning: str
    key_channels: list[str]
    content_style: str


class BrandCreate(BaseModel):
    name: str
    website: str
    industry: str
    target_region: str
    target_audience: str | None = None
    social_profiles: SocialProfilesSchema | None = None


class BrandUpdate(BaseModel):
    name: str | None = None
    website: str | None = None
    industry: str | None = None
    target_region: str | None = None
    target_audience: str | None = None
    social_profiles: SocialProfilesSchema | None = None
    persona: BrandPersonaSchema | None = None


class BrandResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    account_id: UUID
    name: str
    website: str
    industry: str
    target_region: str
    target_audience: str | None
    persona: dict | None
    social_profiles: dict | None
    setup_complete: bool
    created_at: datetime
    updated_at: datetime


class PersonaStatusResponse(BaseModel):
    status: str  # pending | generating | complete | failed
    persona: BrandPersonaSchema | None = None
