from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models import Provider
from schemas import ProviderCreate, ProviderLogin, ChangePasswordSchema
from utils import get_password_hash, verify_password, create_access_token, get_record, create_log


class AuthenticationService:
    @staticmethod
    async def signup(provider: ProviderCreate, db: AsyncSession) -> dict:
        existing_user = await get_record(db, Provider, provider_email=provider.provider_email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = get_password_hash(provider.provider_password)
        new_provider = Provider(
            provider_username=provider.provider_username,
            provider_email=provider.provider_email,
            provider_password=hashed_password
        )

        db.add(new_provider)
        await db.commit()
        await db.refresh(new_provider)
        await create_log(action="Provider signup", provider_id=new_provider.provider_id, db=db)

        return {"message": "Successful"}

    @staticmethod
    async def login(provider: ProviderLogin, db: AsyncSession) -> dict:
        user = await get_record(db, Provider, provider_email=provider.provider_email)
        if user is None:
            raise HTTPException(status_code=401, detail="User does not exist")

        if not verify_password(provider.provider_password, user.provider_password):
            raise HTTPException(status_code=401, detail="Invalid password")

        await create_log(action="Provider login", provider_id=user.provider_id, db=db)
        token = create_access_token(data={"sub": user.provider_email})

        return {
            "access_token": token,
            "token_type": "bearer",
            "provider_id": user.provider_id,
            "provider_username": user.provider_username,
            "provider_email": user.provider_email,
        }

    @staticmethod
    async def logout(provider_id: int, db: AsyncSession) -> dict:
        if not provider_id:
            raise HTTPException(status_code=401, detail="Invalid provider")
        await create_log(action="Provider logout", provider_id=provider_id, db=db)
        return {"message": "Successfully logged out"}


    @staticmethod
    async def change_password(
        password_data: ChangePasswordSchema, db: AsyncSession
    ) -> dict:
        user = await get_record(db, Provider, provider_email=password_data.provider_email)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        # ✅ Remove old_password check if not needed
        hashed_new_password = get_password_hash(password_data.new_password)
        user.provider_password = hashed_new_password
        await db.commit()
        await create_log(action="Password changed", provider_id=user.provider_id, db=db)

        return {"message": "Password successfully changed"}

    @staticmethod
    async def logout(provider_id: int, db: AsyncSession)-> dict:
        if not provider_id:
            raise HTTPException(status_code=401, detail="Invalid provider")

        await create_log(action="Provider logout", provider_id=provider_id, db=db)
        return {"message": "Successfully logged out"}
