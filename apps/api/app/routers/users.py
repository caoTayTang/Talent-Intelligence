from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import bcrypt

from talent_core.db import get_db
from talent_core.models import User
from app.schemas.users import CreateUserRequest, UserResponse, LoginRequest

router = APIRouter()


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    pwd_bytes = password.encode('utf-8')
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False


@router.post("", response_model=UserResponse, status_code=201)
def create_user(
    request: CreateUserRequest,
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    Create a new user with a hashed password.
    Only Candidate role is allowed for public registration.
    """
    if request.role == "hr":
        raise HTTPException(
            status_code=403, 
            detail="Public HR registration is disabled. Please contact an administrator."
        )

    user = User(
        email=request.email,
        name=request.name,
        role=request.role,
        hashed_password=hash_password(request.password)
    )

    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists")

    db.refresh(user)
    return UserResponse.from_model(user)


@router.post("/login", response_model=UserResponse)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
) -> UserResponse:
    user = db.query(User).filter(
        User.email == request.email,
        User.role == request.role
    ).first()
    
    if not user or not user.hashed_password or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail=f"Invalid email, password, or role for {request.role}")

    return UserResponse.from_model(user)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)) -> UserResponse:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse.from_model(user)

