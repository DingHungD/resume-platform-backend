from fastapi import FastAPI
from app.api.v1 import auth, resume 
from app.api.v1.endpoints import chat
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# 統一使用 settings.API_V1_STR (預期值為 "/api/v1")
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])
app.include_router(resume.router, prefix=f"{settings.API_V1_STR}/resume", tags=["Resume Management"])
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["AI Chat"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Resume RAG API"}