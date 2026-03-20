from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.chat_service import chat_service
from app.api.deps import get_current_user_ws # 👈 引用剛寫好的驗證
from app.models.chat import ChatMessage, ChatSession      # 👈 引用對話模型
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
        print(f"🔌 Client disconnected: {session_id}")
    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")

# ---訪客模式 WebSocket (無痕/不存 DB) ---
@router.websocket("/guest/{token}")
async def websocket_guest_chat_endpoint(
    websocket: WebSocket, 
    token: str, 
    db: Session = Depends(get_db)
):
    await websocket.accept()
    
    # A. 驗證 Token 是否有效且開啟分享
    session = db.query(ChatSession).filter(
        ChatSession.share_token == token,
        ChatSession.is_public == True
    ).first()

    if not session:
        await websocket.send_text("Error: Invalid or expired share link")
        await websocket.close(code=4003)
        return

    print(f"👤 Guest connected to session {session.id} via token")

    try:
        while True:
            data = await websocket.receive_text()
            message_json = json.loads(data)
            user_query = message_json.get("message")

            # B. 訪客模式：不存入資料庫，直接進行 RAG 檢索與回答
            try:
                # 直接呼叫 chat_service，傳入 session.id
                async for chunk in chat_service.get_streaming_answer(db, str(session.id), user_query):
                    await websocket.send_text(chunk)
                
                # 發送結束訊號，同樣不寫入資料庫
                await websocket.send_text("[DONE]")
                
            except Exception as inner_e:
                print(f"❌ Guest Chat Error: {traceback.format_exc()}")
                await websocket.send_text(f"Processing Error: {str(inner_e)}")
            
    except WebSocketDisconnect:
        print(f"🔌 Guest disconnected from token: {token}")
    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")
