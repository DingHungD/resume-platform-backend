from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any

class ResumeRead(BaseModel):
    id: UUID
    file_name: str
    file_type: str
    status: str
    created_at: datetime
    session_id: Optional[UUID] = None
    is_public: bool = False
    # 這裡可以選擇性回傳解析後的 JSON，如果還沒解析完就是空
    raw_text: Optional[str] = None
    extracted_info: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True # 讓 Pydantic 可以直接讀取 SQLAlchemy 物件