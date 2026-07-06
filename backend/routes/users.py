# backend/routes/users.py
import uuid
import datetime
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.connection import get_db
from backend.database.models import User
from backend.core.security import hash_password, verify_password, create_access_token, get_current_user_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/users", tags=["users"])


class UserRegisterSchema(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

def _user_dict(user: User) -> dict:
    return {
        "id":              user.id,
        "email":           user.email,
        "username":        user.username,
        "streak_count":    user.streak_count or 0,
        "longest_streak":  user.longest_streak or 0,
        "total_messages":  user.total_messages or 0,
        "created_at":      user.created_at.isoformat() if user.created_at else None,
    }

@router.post("/register")
async def register(data: UserRegisterSchema, db: AsyncSession = Depends(get_db)):
    try:
        q   = select(User).where(User.email == data.email)
        res = await db.execute(q)
        if res.scalars().first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered")

        user_id = f"usr_{uuid.uuid4().hex[:12]}"
        user    = User(
            id=user_id,
            email=data.email,
            username=data.username,
            password_hash=hash_password(data.password),
            created_at=datetime.datetime.utcnow(),
            last_active=datetime.datetime.utcnow(),
            streak_count=0,
            longest_streak=0,
            total_messages=0
        )
        db.add(user)
        await db.commit()

        token = create_access_token({"sub": user_id})
        return {
            "success": True,
            "data": {"access_token": token, "token_type": "bearer", "user": _user_dict(user)},
            "error": None
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"register error: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/login")
async def login(data: UserLoginSchema, db: AsyncSession = Depends(get_db)):
    try:
        q    = select(User).where(User.email == data.email)
        res  = await db.execute(q)
        user = res.scalars().first()
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

        user.last_active = datetime.datetime.utcnow()
        await db.commit()

        token = create_access_token({"sub": user.id})
        return {
            "success": True,
            "data": {"access_token": token, "token_type": "bearer", "user": _user_dict(user)},
            "error": None
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"login error: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Login failed")

@router.get("/me")
async def get_me(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    try:
        q    = select(User).where(User.id == user_id)
        res  = await db.execute(q)
        user = res.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"success": True, "data": _user_dict(user), "error": None}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"get_me error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user profile")
