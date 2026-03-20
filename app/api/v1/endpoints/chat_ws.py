from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.chat_service import chat_service
from app.api.deps import get_current_user_ws # 👈 引用剛寫好的驗證
from app.models.chat import ChatMessage      # 👈 引用對話模型
import json
import traceback
from uuid import UUID

router = APIRouter()

@router.websocket("/chat/{session_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket, 
    session_id: str, 
    db: Session = Depends(get_db)
):

    
    
    await websocket.accept()
        # 1. 驗證身分
    current_user = await get_current_user_ws(websocket, db)
    if not current_user:
        await websocket.send_text("Error: Unauthorized")
        await websocket.close(code=4003)
        return
    print(f"✅ User {current_user.email} connected to resume {session_id}")
    
    try:
        while True:
            data = await websocket.receive_text()
            message_json = json.loads(data)
            user_query = message_json.get("message")

            # 2. 持久化：存入 User 的問題
            try:
                user_msg = ChatMessage(
                    resume_id=session_id,
                    user_id=current_user.id,
                    role="user",
                    content=user_query
                )
                db.add(user_msg)
                db.commit()

                # 3. 串流 AI 回答並紀錄
                full_ai_response = ""
                async for chunk in chat_service.get_streaming_answer(db, session_id, user_query):
                    full_ai_response += chunk
                    await websocket.send_text(chunk)
                
                # 4. 持久化：存入 AI 的完整回答
                ai_msg = ChatMessage(
                    resume_id=session_id,
                    user_id=current_user.id,
                    role="assistant",
                    content=full_ai_response
                )
                db.add(ai_msg)
                db.commit()

                # 5. 發送結束訊號
                await websocket.send_text("[DONE]")
            except Exception as inner_e:
                db.rollback() # ⚠️ 發生資料庫錯誤一定要回滾
                print(f"❌ DB/Service Error: {traceback.format_exc()}")
                await websocket.send_text(f"Processing Error: {str(inner_e)}")
            
    except WebSocketDisconnect:
        print(f"🔌 Client disconnected: {resume_id}")
    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")