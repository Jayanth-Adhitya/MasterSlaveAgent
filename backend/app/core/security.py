from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import get_settings
from app.schemas.auth import TokenData

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def decode_access_token(token: str) -> TokenData | None:
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        user_id = payload.get("user_id")
        tenant_id = payload.get("tenant_id")
        email = payload.get("email")
        name = payload.get("name")
        role = payload.get("role")
        tenant_name = payload.get("tenant_name")
        tenant_type = payload.get("tenant_type")

        if user_id is None or tenant_id is None:
            return None

        return TokenData(
            user_id=user_id,
            tenant_id=tenant_id,
            email=email,
            name=name,
            role=role,
            tenant_name=tenant_name,
            tenant_type=tenant_type,
        )
    except JWTError:
        return None
