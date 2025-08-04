from pydantic import BaseModel, EmailStr
import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None
    created_at: datetime.datetime
    token: Token

    class Config:
        from_attributes = True
