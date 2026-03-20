from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.chat import ChatMessage
from app.schemas.chat import ChatMessageOut

router = APIRouter()

@router.get("/{resume_id}/history", response_model=List[ChatMessageOut])
def get_chat_history(
    resume_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    獲取特定履歷的歷史對話紀錄，並確保只能看到自己的
    """
    messages = db.query(ChatMessage).filter(
        ChatMessage.resume_id == resume_id,
        ChatMessage.user_id == current_user.id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    return messages