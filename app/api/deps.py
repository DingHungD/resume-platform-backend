from fastapi import Depends, HTTPException, status, WebSocket
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_current_user(
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None: raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None: raise credentials_exception
    return user

# ✨ 新增：WebSocket 專用驗證 (從 Query Parameter 拿 Token)
async def get_current_user_ws(websocket: WebSocket, db: Session) -> User:
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return None
        return user
    except JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None