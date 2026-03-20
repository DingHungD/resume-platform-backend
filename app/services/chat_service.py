from sqlalchemy.orm import Session
from app.models.resume import DocumentChunk
from app.services.ai_service import ai_service
from pgvector.sqlalchemy import Vector
from app.models.resume import Resume

class ChatService:
    def __init__(self):
        pass

    async def get_answer(self, db: Session, resume_id: str, query: str):
        # 1. 將用戶的問題轉為向量 (1536維)
        query_embedding = await ai_service.get_embedding(query)

        # 2. 向量檢索：從資料庫撈出最相關的 5 個片段 (Cosine Similarity)
        # 注意：resume_id 用來過濾，確保不跨人搜尋
        chunks = db.query(DocumentChunk).filter(
            DocumentChunk.resume_id == resume_id
        ).order_by(
            DocumentChunk.embedding.cosine_distance(query_embedding)
        ).limit(5).all()

        if not chunks:
            return "找不到相關的履歷內容，請確認履歷是否已正確上傳並解析。"

        # 3. 組合 Context 內容
        context_text = "\n".join([c.content for c in chunks])

        # 4. 構建 Prompt 給 LLM
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
    async def get_streaming_answer(self, db: Session, resume_id: str, query: str):
        # 1. 執行向量檢索 (Retrieval)
        query_embedding = await ai_service.get_embedding(query)
        chunks = db.query(DocumentChunk).filter(
            DocumentChunk.resume_id == resume_id
        ).order_by(
            DocumentChunk.embedding.cosine_distance(query_embedding)
        ).limit(5).all()

        context = "\n".join([c.content for c in chunks])
        
        # 2. 組合 Prompt 
        full_prompt = f"以下是該候選人的履歷相關片段：\n{context}\n\n請回答問題：{query}"

        # 3. 呼叫 AI 串流產生器 (Generation)
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