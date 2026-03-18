from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

# 註冊請求
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

# 登入回應
class Token(BaseModel):
    access_token: str
    token_type: str

# API 回傳的使用者資料 (不含密碼)
class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    full_name: Optional[str] = None

    class Config:
        from_attributes = True