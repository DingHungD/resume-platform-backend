from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Optional

class ChatMessageBase(BaseModel):
    content: str
    role: str

class ChatMessageCreate(ChatMessageBase):
    resume_id: UUID

class ChatMessageOut(ChatMessageBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class ChatHistory(BaseModel):
    resume_id: UUID
    messages: List[ChatMessageOut]