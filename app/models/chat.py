from sqlalchemy import Column, String, Text, DateTime, ForeignKey, UUID, Boolean
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.db.session import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=True) # 例如：某次面試的分析
    created_at = Column(DateTime, default=datetime.utcnow)

    # --- 訪客模式新增欄位 ---
    is_public = Column(Boolean, default=False, index=True) # 是否開啟公開分享
    share_token = Column(String, unique=True, index=True, nullable=True) # 公開分享用的唯一 Token
    
    # 可選：訪客模式權限設定 (例如：是否允許訪客提問，還是僅限查看)
    guest_can_chat = Column(Boolean, default=True)

    # 關聯：一個 Session 有多則訊息，且有多份履歷
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="session")
    user = relationship("User", back_populates="chat_sessions")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # 關聯到履歷 ID
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=True)
    # 關聯到使用者 ID (確保資料隔離)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    # 關聯到 Session 而非單一 Resume
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)

    role = Column(String, nullable=False) # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 建立關聯
    session = relationship("ChatSession", back_populates="messages")
    resume = relationship("Resume", back_populates="messages")
    user = relationship("User", back_populates="chat_messages")