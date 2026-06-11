from uuid import UUID
from datetime import datetime

from pydantic import BaseModel

from talent_core.models import Company


class CreateCompanyRequest(BaseModel):
    name: str
    logo_url: str | None = None
    website: str | None = None


class CompanyResponse(BaseModel):
    id: UUID
    name: str
    logo_url: str | None = None
    website: str | None = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, company: Company) -> "CompanyResponse":
        return cls(
            id=company.id,
            name=company.name,
            logo_url=company.logo_url,
            website=company.website,
            created_at=company.created_at,
            updated_at=company.updated_at,
        )

