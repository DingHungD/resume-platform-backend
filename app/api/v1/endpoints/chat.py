from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.chat_service import chat_service
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    resume_id: str
    message: str

@router.post("/query")
async def chat_with_resume(
    request: ChatRequest, 
    db: Session = Depends(get_db)
):
    try:
        answer = await chat_service.get_answer(
            db, 
            resume_id=request.resume_id, 
            query=request.message
        )
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))