"""Authentication endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.schemas.auth import Token, LoginRequest
from app.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(
    request: LoginRequest, session: AsyncSession = Depends(get_db)
) -> Token:
    """Authenticate user and return JWT token."""
    # Find user by email with tenant eagerly loaded
    result = await session.execute(
        select(User).where(User.email == request.email).options(selectinload(User.tenant))
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Tenant is already loaded
    tenant = user.tenant

    # Create JWT token with user and tenant info
    token_data = {
        "user_id": user.id,
        "tenant_id": user.tenant_id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "tenant_name": tenant.name,
        "tenant_type": tenant.type,
    }

    access_token = create_access_token(token_data)

    return Token(access_token=access_token)
