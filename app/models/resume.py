import uuid
from sqlalchemy import Column, String, ForeignKey, JSON, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.session import Base
from sqlalchemy.sql import text
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import relationship

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="SET NULL"), nullable=True)
    
    # 檔案系統相關
    file_name = Column(String, nullable=False)  # 原始檔名
    file_path = Column(String, nullable=False)  # 儲存在伺服器上的路徑 (例如: /uploads/abc.pdf)
    file_type = Column(String)                  # .pdf, .docx, .txt
    
    # AI 提取的基本資料 (姓名、年齡、性別、技能等全部塞這裡)
    extracted_info = Column(JSON, default={})
    
    # 原始純文字 (供 RAG 切片前備份)
    raw_text = Column(Text, nullable=True)
    
    # 狀態追蹤
    status = Column(String, default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    messages = relationship("ChatMessage", back_populates="resume", cascade="all, delete-orphan")
    user = relationship("User", back_populates="resumes")
    session = relationship("ChatSession", back_populates="resumes")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"))
    content = Column(Text)
    embedding = Column(Vector(1536)) # 對應 OpenAI embedding 維度
    
    