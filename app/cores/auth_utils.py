from jose import JWTError, ExpiredSignatureError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.cores import auth
from app.models.users import User

def validate_token_and_get_user(token: str, db: Session) -> User:
    try:
        payload = auth.decode_token(token)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

        user = db.query(User).filter(User.username == username).first()
        if not user or not user.status:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User blocked or not found")

        return user

    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token expired")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

