from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from talent_core.db import get_db
from talent_core.models import User
from app.schemas.users import CreateUserRequest, UserResponse

router = APIRouter()


@router.post("", response_model=UserResponse, status_code=201)
def create_user(
    request: CreateUserRequest,
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    Create a temporary user for local development.

    This is not authentication. It only creates a User row so jobs,
    applications, and agent flows can reference candidate_id / hr_id.
    """
    user = User(
        email=request.email,
        name=request.name,
        role=request.role,
    )

    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists")

    db.refresh(user)
    return UserResponse.from_model(user)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)) -> UserResponse:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse.from_model(user)

