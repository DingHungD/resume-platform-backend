from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.chat import ChatMessage, ChatSession
from app.schemas.chat import ChatMessageOut

router = APIRouter()

@router.get("/{session_id}/history", response_model=List[ChatMessageOut])
def get_chat_history(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    獲取特定履歷的歷史對話紀錄，並確保只能看到自己的
    """
    # 增加一層安全檢查，確保該 session 屬於當前用戶
    session_exists = db.query(ChatSession).filter(
        ChatSession.id == session_id, 
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session_exists:
        raise HTTPException(status_code=404, detail="Chat session not found")

    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id, # 改用 session_id 過濾
        ChatMessage.user_id == current_user.id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    return messages

@router.get("/sessions/{session_id}")
async def get_session_detail(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """供前端對話室載入時獲取分享狀態與詳情"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    return {
        "id": session.id,
        "title": session.title,
        "is_public": session.is_public,
        "share_token": session.share_token,
        "guest_can_chat": session.guest_can_chat,
        "created_at": session.created_at
    }
