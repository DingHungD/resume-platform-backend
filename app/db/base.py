# 用來讓 Alembic 看到所有模型
from app.db.session import Base  # noqa
from app.models.user import User  # noqa
from app.models.resume import Resume, DocumentChunk  # noqa
from app.models.chat import ChatSession, ChatMessage