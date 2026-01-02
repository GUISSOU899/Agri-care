from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    email: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class UserBase(BaseModel):
    email: Optional[str] = None
    is_active: Optional[bool] = True
    role: str = "user"

class UserCreate(UserBase):
    email: str
    password: str

class UserRead(UserBase):
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserInDB(UserRead):
    hashed_password: str
