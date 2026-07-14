from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

ACADEMIC_LEVELS = [
    "School Student",
    "Intermediate / Higher Secondary",
    "Undergraduate",
    "Postgraduate",
    "Self Learner",
    "Educator",
]


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str
    academic_level: str

    @field_validator("academic_level")
    @classmethod
    def validate_level(cls, v):
        if v not in ACADEMIC_LEVELS:
            raise ValueError(f"academic_level must be one of {ACADEMIC_LEVELS}")
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    academic_level: str
    created_at: datetime

    model_config = {"from_attributes": True}


TokenResponse.model_rebuild()
