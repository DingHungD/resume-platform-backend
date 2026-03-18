from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 依賴注入：獲取資料庫連線
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()