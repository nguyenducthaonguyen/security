from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.cores import auth
from app.cores.dependencies import get_db
from app.models.users import User
from app.schemas.users import UserCreate, UserRead, TokenResponse

router = APIRouter()

@router.post("/register", response_model=UserRead)
def register(user: UserCreate, db: Session = Depends(get_db)):
    user_username = db.query(User).filter(User.username == user.username).first()
    if user_username:
        raise HTTPException(status_code=400, detail="Username already exists")
    user_email = db.query(User).filter(User.email == user.email).first()
    if user_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    hashed = auth.get_password_hash(user.password)
    new_user = User(username=user.username, password=hashed, email=user.email,fullname=user.fullname, gender=user.gender)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.password):
        raise HTTPException(401, "Invalid credentials")
    if not user.status:
        raise HTTPException(401, "User block")

    token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer", "id": user.id, "username": user.username}


