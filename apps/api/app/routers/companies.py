from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from talent_core.db import get_db
from talent_core.models import Company
from app.schemas.companies import CreateCompanyRequest, CompanyResponse

router = APIRouter()


@router.post("", response_model=CompanyResponse, status_code=201)
def create_company(
    request: CreateCompanyRequest,
    db: Session = Depends(get_db),
) -> CompanyResponse:
    """
    Create a company that can own jobs.
    """
    company = Company(
        name=request.name,
        logo_url=request.logo_url,
        website=request.website,
    )

    db.add(company)
    db.commit()
    db.refresh(company)

    return CompanyResponse.from_model(company)


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: UUID,
    db: Session = Depends(get_db),
) -> CompanyResponse:
    """
    Return one company by ID.
    """
    company = db.get(Company, company_id)

    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    return CompanyResponse.from_model(company)

