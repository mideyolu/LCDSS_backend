#### app/utils.py

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from models import Log
from datetime import datetime, timedelta
from config import settings
from models import Provider
from database import get_db
from typing import Optional
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "provider_id": data["sub"]})  # Add provider_id to the payload
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def create_log(action: str, provider_id: int, db: AsyncSession):
    """Creates a log entry for an action."""
    try:

            log_entry = Log(
                action=action,
                created_at=datetime.utcnow(),
                provider_id=provider_id
            )
            db.add(log_entry)
            await db.commit()
    except Exception as e:
        print(f"Failed to create log: {str(e)}")

async def get_current_provider(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        # Decode the JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        provider_email: str = payload.get("sub")  # This will return the email

        if provider_email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")

        # Retrieve provider_id using email
        query = select(Provider).where(Provider.provider_email == provider_email)
        result = await db.execute(query)  # This needs to be awaited in an async function
        provider = result.scalars().first()  # Get the first matching provider

        if provider is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")

        return provider.provider_id  # Return the provider_id

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Verify access token
def verify_access_token(token: str) -> Optional[dict]:
    try:
        # Use jwt.decode directly
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload  # Decoded token payload
    except JWTError:
        return None


async def get_record(db: AsyncSession, model, **filters):
    """Retrieve a single record from the database based on filters."""
    query = select(model).filter_by(**filters)
    result = await db.execute(query)
    return result.scalars().first()

async def get_count(db: AsyncSession, model, **filters):
    """Count the number of records in a model based on filters."""
    query = select(func.count()).select_from(model).filter_by(**filters)
    result = await db.execute(query)
    return result.scalar() or 0
