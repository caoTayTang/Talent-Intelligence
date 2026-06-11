from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, EmailStr

from talent_core.models import User, UserRole


class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str
    role: UserRole


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    role: str
    is_active: bool
    created_at: datetime

    @classmethod
    def from_model(cls, user: User) -> "UserResponse":
        return cls(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
        )

