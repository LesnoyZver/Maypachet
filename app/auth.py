import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from authx import AuthX, AuthXConfig, TokenPayload
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import async_session_maker
from models import User, Equipment, EquipmentType


load_dotenv()

config = AuthXConfig(
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY"),
    JWT_ACCESS_COOKIE_NAME = "maypachet_access_token",
    JWT_TOKEN_LOCATION = ['cookies'],
    JWT_COOKIE_CSRF_PROTECT=False,
    JWT_COOKIE_SECURE=False
)

security = AuthX(config=config)

pwd_context = CryptContext(schemes=["argon2"])


async def get_user_login(payload: TokenPayload = Depends(security.access_token_required)) -> str:
    return payload.sub

class Auth:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def register_user(self, login, password) -> dict:
        existing = await self.session.scalar(select(User).where(User.login == login))
        if existing is None:
            password_hash = pwd_context.hash(password)
            user = User(login=login, password_hash=password_hash)
            self.session.add(user)
            await self.session.commit()
            return {"Registration": "Success", "Status": "OK"}
        else:
            raise HTTPException(status_code=409, detail="User already exists!")

    async def auth_user(self, login: str, password: str):
        password_hash = await self.session.scalar(select(User.password_hash).where(User.login == login))
        if password_hash is None:
            raise HTTPException(status_code=404, detail="User not found!")
        if pwd_context.verify(password ,password_hash):
            access_token = security.create_access_token(uid=login)
            return access_token
        else:
            raise HTTPException(status_code=403, detail="Password doesn't match")

    async def change_user_password(self, login: str, password: str, new_password: str):
        password_hash = await self.session.scalar(select(User.password_hash).where(User.login == login))
        if password_hash is None:
            raise HTTPException(status_code=404, detail="User not found!")
        if not pwd_context.verify(password, password_hash):
            raise HTTPException(status_code=403, detail="Password doesn't match.")
        if pwd_context.verify(new_password, password_hash):
            raise HTTPException(status_code=403, detail="The password must be different.")
        new_password_hash = pwd_context.hash(new_password)
        user_obj = await self.session.execute(select(User).where(User.login == login))
        user = user_obj.scalar_one_or_none()
        user.password_hash = new_password_hash
        await self.session.commit()
        return user