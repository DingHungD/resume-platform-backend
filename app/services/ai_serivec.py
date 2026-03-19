from openai import OpenAI
from app.core.config import settings
from typing import Dict, Any
from app.schemas.analysis import ResumeAnalysisResult # 引入剛定義的格式

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        # 建議使用 gpt-4o 或 gpt-4o-mini，它們對 Structured Outputs 支援最好
        self.model = "gpt-4o-mini"

    def analyze_resume(self, text: str) -> Dict[str, Any]:
        """
        使用 Structured Outputs 強制要求 AI 依照 Pydantic 模型回傳
        """
        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位專業的獵頭顧問，負責從履歷中精確提取結構化資訊。"},
                    {"role": "user", "content": f"請解析以下履歷內容：\n\n{text}"}
                ],
                # 這裡就是魔法所在：傳入 Pydantic 類別
                response_format=ResumeAnalysisResult, 
            )
            
            # 直接取得驗證過後的 Pydantic 物件
            analysis_result = completion.choices[0].message.parsed
            
            # 轉成 Dictionary 回傳，方便存入資料庫的 JSONB 欄位
            return analysis_result.model_dump()
            
        except Exception as e:
            print(f"❌ AI 結構化解析失敗: {str(e)}")
            # 回傳基礎格式避免程式崩潰
            return {
                "name": "Unknown",
                "error": str(e),
                "status": "parsing_error"
            }
    async def get_embedding(self, text: str):
        response = await self.client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding

    async def call_llm(self, prompt: str):
        response = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

# 實例化
ai_service = AIService()