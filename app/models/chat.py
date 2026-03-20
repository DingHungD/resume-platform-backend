from sqlalchemy import Column, String, Text, DateTime, ForeignKey, UUID
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

    # 關聯：一個 Session 有多則訊息，且有多份履歷
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="session")
    user = relationship("User", back_populates="chat_sessions")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # 關聯到履歷 ID
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
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