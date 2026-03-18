import os
import uuid
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.resume import Resume

router = APIRouter()

# 定義上傳資料夾
UPLOAD_DIR = "uploads/resumes"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    # 1. 產生唯一檔名，避免重複
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    dest_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # 2. 將檔案寫入磁碟
    with open(dest_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # 3. 在資料庫建立紀錄
    new_resume = Resume(
        user_id=None,  # 待整合 Auth 後自動填入
        file_name=file.filename,
        file_path=dest_path,
        file_type=file_ext,
        extracted_info={}, # 初始為空，等 Worker 提取後填入
        status="pending"
    )
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)
    
    # 4. TODO: 發送任務給 Celery Worker (Repo C) 進行解析
    
    return {"message": "Upload successful", "resume_id": str(new_resume.id)}