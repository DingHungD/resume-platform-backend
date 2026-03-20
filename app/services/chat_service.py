from sqlalchemy.orm import Session
from app.models.resume import DocumentChunk, Resume
from app.services.ai_service import ai_service
from pgvector.sqlalchemy import Vector
from typing import List

class ChatService:
    def __init__(self):
        pass

    async def _get_session_resume_ids(self, db: Session, session_id: str) -> List[str]:
        """封裝：獲取該 Session 下所有已就緒的履歷 ID"""
        resumes = db.query(Resume.id).filter(
            Resume.session_id == session_id,
            Resume.status == 'completed' # 只檢索解析完成的
        ).all()
        return [str(r.id) for r in resumes]

    async def get_answer(self, db: Session, session_id: str, query: str):
        # 1. 將用戶的問題轉為向量 (1536維)
        query_embedding = await ai_service.get_embedding(query)

        # 2. 找出該 Session 關聯的所有履歷 ID
        resume_ids = await self._get_session_resume_ids(db, session_id)
        if not resume_ids:
            return "目前此對話尚未關聯任何已完成解析的履歷資料，請稍候或上傳檔案。"
        
        # 3. 向量檢索：使用 .in_(resume_ids) 進行多檔案搜尋
        chunks = db.query(DocumentChunk).filter(
            DocumentChunk.resume_id.in_(resume_ids) # 支援多檔案檢索
        ).order_by(
            DocumentChunk.embedding.cosine_distance(query_embedding)
        ).limit(7).all() # 稍微增加 找到的chunk數量 is can change arg

        if not chunks:
            return "在目前的履歷庫中找不到與您問題相關的內容。"

        # 4. 組合 Context 內容
        context_text = "\n".join([c.content for c in chunks])

        # 5. 構建 Prompt 給 LLM
        prompt = f"""
你是一位專業的人資助理，請根據以下提供的「履歷片段內容」來回答用戶的問題。
如果內容中沒有提到相關資訊，請誠實回答不知道，不要編造事實。

【履歷參考內容】：
{context_text}

【用戶問題】：
{query}

請用簡潔專業的口吻回答：
"""

        # 5. 呼叫 LLM 產生回應 (假設你的 ai_service 有 call_llm 方法)
        answer = await ai_service.call_llm(prompt)
        return answer
    
    async def get_streaming_answer(self, db: Session, session_id: str, query: str):
        # 1. 執行向量檢索 (Retrieval)
        query_embedding = await ai_service.get_embedding(query)

        # 2. 找出該 Session 關聯的所有履歷 ID
        resume_ids = await self._get_session_resume_ids(db, session_id)

        # 3. 向量檢索：使用 .in_(resume_ids) 進行多檔案搜尋
        chunks = db.query(DocumentChunk).filter(
            DocumentChunk.resume_id.in_(resume_ids)
        ).order_by(
            DocumentChunk.embedding.cosine_distance(query_embedding)
        ).limit(7).all()

        context = "\n".join([c.content for c in chunks])
        
        # 4. 組合 Prompt 
        full_prompt = f"以下是該候選人的履歷相關片段：\n{context}\n\n請回答問題：{query}"

        # 5. 呼叫 AI 串流產生器 (Generation)
        async for char in ai_service.stream_chat(full_prompt):
            yield char

    async def delete_resume(self, db: Session, resume_id: str, user_id: str) -> bool:
        """
        刪除履歷及其關聯的所有數據 (Chunks/Vectors, Messages)
        """
        # 1. 查找並驗證權限
        resume = db.query(Resume).filter(
            Resume.id == resume_id,
            Resume.user_id == user_id
        ).first()

        if not resume:
            return False

        try:
            # 2. 執行刪除 (資料庫設定了 CASCADE 會自動刪除 Chunks 與 Messages)
            db.delete(resume)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"❌ 刪除履歷失敗: {str(e)}")
            return False

chat_service = ChatService()