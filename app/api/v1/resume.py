import os
import uuid
import aiofiles
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.db.session import get_db
from app.models.resume import Resume
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.resume import ResumeRead
from app.worker import analyze_resume_task
from app.services.chat_service import chat_service
from app.models.chat import ChatSession

router = APIRouter()

# 設定上傳路徑
UPLOAD_DIR = "uploads/resumes"
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
os.makedirs(UPLOAD_DIR, exist_ok=True)

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/upload", status_code=status.HTTP_201_CREATED, response_model=ResumeRead)
async def upload_resume(
    file: UploadFile = File(...), 
    session_id: Optional[UUID] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. 檢查檔案格式
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {ALLOWED_EXTENSIONS}"
        )
    # 2. 處理 ChatSession 邏輯
    if session_id:
        # 檢查該 Session 是否屬於目前使用者
        chat_session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        ).first()
        if not chat_session:
            raise HTTPException(status_code=404, detail="Chat session not found")
    else:
        # 如果沒有傳 session_id，自動建立一個新的對話會話
        chat_session = ChatSession(
            id=uuid.uuid4(),
            user_id=current_user.id,
            title=f"Chat: {file.filename}"
        )
        db.add(chat_session)
        db.flush() # 先取得 ID 供後續 Resume 綁定

    # 3. 產生唯一檔名與路徑
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    dest_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # 4. 異步寫入檔案到磁碟
    try:
        content = await file.read()
        async with aiofiles.open(dest_path, mode="wb") as f:
            await f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(e)}"
        )
    
    # 5. 在資料庫建立紀錄
    new_resume = Resume(
        id=uuid.uuid4(),
        user_id=current_user.id,  # 成功關聯目前登入用戶
        session_id=chat_session.id, # 關聯到 Session
        file_name=file.filename,
        file_path=dest_path,
        file_type=file_ext,
        extracted_info={},        # 初始為空
        status="processing"       # 改為處理中
    )
    
    try:
        db.add(new_resume)
        db.commit()
        db.refresh(new_resume)
        # 6. 發送任務給 Celery Worker (Repo C)
        print(f"📡 正在發送任務至 Redis: {new_resume.id}")
        analyze_resume_task.delay(str(new_resume.id), dest_path)
        print(f"✅ 任務已發出，Task ID: {new_resume.id}")
    except Exception as e:
        # 如果資料庫寫入失敗，應刪除已上傳的實體檔案
        if os.path.exists(dest_path):
            os.remove(dest_path)
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

    
    return new_resume

@router.get("/", response_model=List[ResumeRead])
async def list_my_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 10
):
    """
    取得當前登入使用者的所有履歷列表
    """
    resumes = db.query(Resume)\
        .filter(Resume.user_id == current_user.id)\
        .order_by(Resume.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return resumes

@router.get("/{resume_id}", response_model=ResumeRead)
async def get_resume_detail(
    resume_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    取得特定單一履歷的詳細資訊
    """
    resume = db.query(Resume).filter(
        Resume.id == resume_id, 
        Resume.user_id == current_user.id
    ).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    return resume

@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    success = await chat_service.delete_resume(db, resume_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Resume not found or unauthorized")
    return None

@router.get("/sessions")
async def get_user_sessions(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """讓前端 Dashboard 列出所有對話列表"""
    sessions = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).all()
    return sessions
