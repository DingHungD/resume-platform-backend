# Resume RAG API (Backend)

## 📌 項目概述
本專案是 **AI-Powered Resume RAG Platform** 的後端核心服務。它負責處理所有商業邏輯、資料庫交互、PDF 語意解析以及與大型語言模型 (LLM) 的整合。

- **核心語言**: Python 3.11+ (主要框架：FastAPI)
- **它的作用**: 
  - 提供 RESTful API 供前端呼叫。
  - 處理履歷上傳並自動進行文字切片 (Chunking)。
  - 整合 OpenAI Embedding 將履歷轉化為向量並存入 PostgreSQL (pgvector)。
  - 實現基於 RAG (檢索增強生成) 的智能問答接口。
- **為什麼有用**: 
  它將傳統的靜態履歷轉化為可查詢的知識庫，讓招募人員能以自然語言對話的方式，從成千上萬份履歷中精確定位符合特定技能與經驗的人才。

---

## 🛠️ 安裝要求
在本地環境開發前，請確保已安裝以下工具：
- **Python**: 3.11 或更高版本
- **pip**: Python 套件管理器
- **Virtualenv**: (強烈建議) 用於隔離專案依賴
- **PostgreSQL**: 需支援 `pgvector` 擴充功能（若使用 Docker 部署則不需單獨安裝）

---

## 📖 安裝與配置文檔
本後端服務通常與部署環境緊密結合，請參考以下文檔以獲得完整資訊：
- [全系統部署指南 (Deploy Repo)](https://github.com/DingHungD/resume-platform-deploy/blob/main/README.md)
- [詳細技術架構設計](https://github.com/DingHungD/resume-platform-deploy/blob/main/ARCHITECTURE.md)

---

## 🚀 使用概述 (開發模式)

1. **環境初始化**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows 使用 venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. **資料庫遷移 (Alembic):**
確保資料庫已啟動，並在 app/core/config.py 或 .env 配置好連線資訊後執行：
   ```bash
   alembic upgrade head
   ```
3. **啟動 API 服務:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   啟動後可訪問 http://localhost:8000/docs 查看 Swagger API 文檔。

---

## 🚀 使用概述 (開發模式)
- Alembic 報錯: 若出現 NameError 或 ModuleNotFoundError，請檢查 alembic/env.py 是否已正確匯入 app.models。
- 向量型別錯誤: 若資料庫報錯 type "vector" does not exist，請確保已執行 CREATE EXTENSION vector;。
- 單元測試: 使用 pytest 進行測試（開發中）。
- 更多細節請參閱 故障排除手冊。

--- 
## 🔗 更多資源
- [FastAPI 官方文檔](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 說明書](https://docs.sqlalchemy.org/)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
