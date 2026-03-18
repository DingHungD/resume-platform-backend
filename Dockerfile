FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴 (編譯 psycopg2 可能需要)
RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# 安裝 Python 套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式碼
COPY . .

# 啟動命令 (注意：與 docker-compose 對接，我們監聽 8000 port)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]