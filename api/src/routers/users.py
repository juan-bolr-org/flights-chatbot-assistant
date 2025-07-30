from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import UserCreate, UserLogin, Token, UserResponse
from models import User
from utils import get_db, get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(
        name=user.name,
        email=user.email,
        password_hash=hashed_password,
        phone=user.phone
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": new_user.email})
    # Here we should sent the email if we have enough time :3
    return Token(access_token=access_token, token_type="bearer")

@router.post("/login", response_model=UserResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": db_user.email})
    return UserResponse(
        id=db_user.id,
        name=db_user.name,
        email=db_user.email,
        phone=db_user.phone,
        created_at=db_user.created_at,
        token=Token(access_token=access_token, token_type="bearer")
    )