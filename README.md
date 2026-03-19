# Resume RAG API (Backend)

## 📌 項目概述
本專案是 **AI-Powered Resume RAG Platform** 的後端核心服務。作為系統的「大腦」，負責處理商業邏輯、身份安全驗證、非同步任務排程以及與大型語言模型 (LLM) 的整合。

* **核心技術棧**: Python 3.11+ / FastAPI / SQLAlchemy 2.0 / Celery / PostgreSQL
* **關鍵功能**: 
    * **安全驗證**: 基於 OAuth2 與 JWT Token 的使用者登入與權限控管。
    * **非同步處理**: 整合 **Redis + Celery**，在上傳履歷後立即回傳結果，並在背景執行耗時的 AI 解析任務。
    * **語意檢索 (RAG)**: 將履歷切片並轉化為向量存入 PostgreSQL (pgvector)，實現自然語言人才搜尋。



## 🛠️ 環境要求
開發與運行前請確保已安裝：
* **Docker & Docker Compose**: (推薦) 用於一鍵啟動 PostgreSQL 與 Redis。
* **Python 3.11+**
* **PostgreSQL**: 需具備 `pgvector` 擴充功能。
* **Redis**: 作為 Celery 的任務代理 (Message Broker)。



## 📖 安裝與配置文檔
本後端服務通常與部署環境緊密結合，請參考以下文檔以獲得完整資訊：
- [全系統部署指南 (Deploy Repo)](https://github.com/DingHungD/resume-platform-deploy/blob/main/README.md)
- [詳細技術架構設計](https://github.com/DingHungD/resume-platform-deploy/blob/main/ARCHITECTURE.md)



## ⚙️ 開發環境啟動 (Quick Start)

### 1. 基礎設施啟動
請切換至 `resume-platform-deploy` 目錄並啟動容器：
而該專案的配置將寫在Dockerfile中，啟動後可訪問 http://localhost:8000/docs 查看 Swagger API 文檔。
   ```bash
   docker-compose up -d
   ```
### 2. **資料庫遷移 (Alembic):**
確保資料庫已啟動，並在 app/core/config.py 或 `resume-platform-deploy`底下的.env 配置好連線資訊後執行：
   ```bash
   docker-compose exec backend alembic upgrade head
   ```


## 🏗️ 系統架構簡述
為了維持高效能與良好的使用者體驗，本專案採用 **Producer-Consumer (生產者-消費者)** 模型：
1.  **FastAPI (Repo A)**: 接收使用者請求，儲存檔案並在資料庫建立 `processing` 紀錄，隨即發送任務至 Redis。
2.  **Redis**: 作為中繼站（Broker），暫存解析任務。
3.  **Celery Worker (Repo C)**: 背景監聽 Redis，領取任務後執行 PDF 解析、OpenAI 提取，並更新資料庫結果。



## 🔍 故障排除與測試提示
- Alembic 報錯: 若出現 NameError 或 ModuleNotFoundError，請檢查 alembic/env.py 是否已正確匯入 app.models。
- 向量型別錯誤: 若資料庫報錯 type "vector" does not exist，請確保已執行 CREATE EXTENSION vector;。
- 單元測試: 使用 pytest 進行測試（開發中）。
- 更多細節請參閱 [故障排除手冊。]()


## 🔗 更多資源
- [FastAPI 官方文檔](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 說明書](https://docs.sqlalchemy.org/)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
