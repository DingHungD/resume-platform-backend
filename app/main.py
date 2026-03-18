from fastapi import FastAPI
from app.api.v1 import auth, resume, chat
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# 掛載路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(resume.router, prefix="/api/v1/resume", tags=["Resume Management"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["AI Chat"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Resume RAG API"}