import os
import uuid
import aiofiles  # 建議 pip install aiofiles
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.resume import Resume
from app.models.user import User
from app.api.v1.auth import get_current_user  # 確保你已實作此 Dependency
# from app.worker import analyze_resume_task  # 假設這是你的 Celery task

router = APIRouter()

# 設定上傳路徑
UPLOAD_DIR = "uploads/resumes"
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...), 
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

    # 2. 產生唯一檔名與路徑
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    dest_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # 3. 異步寫入檔案到磁碟
    try:
        content = await file.read()
        async with aiofiles.open(dest_path, mode="wb") as f:
            await f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(e)}"
        )
    
    # 4. 在資料庫建立紀錄
    new_resume = Resume(
        id=uuid.uuid4(),
        user_id=current_user.id,  # 成功關聯目前登入用戶
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
    except Exception as e:
        # 如果資料庫寫入失敗，應刪除已上傳的實體檔案
        if os.path.exists(dest_path):
            os.remove(dest_path)
        raise HTTPException(status_code=500, detail="Database error")

    # 5. TODO: 發送任務給 Celery Worker (Repo C)
    # analyze_resume_task.delay(str(new_resume.id), dest_path)
    
    return {
        "message": "Upload successful, processing started.",
        "resume_id": str(new_resume.id),
        "filename": file.filename
    }

@router.get("/my-resumes")
async def list_user_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """取得當前使用者上傳的所有履歷狀態"""
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    return resumes



@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # 這裡會自動擋下未登入者
):
    # 此時 current_user 已經是資料庫裡的 User 物件了
    print(f"User {current_user.email} is uploading a file")
    
    # 建立 Resume 時直接關聯：user_id=current_user.id
    ...
