from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from bson import ObjectId

from database import users_collection

load_dotenv()

# ==========================
# CONFIG
# ==========================

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# ==========================
# PASSWORD
# ==========================

def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# ==========================
# JWT
# ==========================

def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.now(
        timezone.utc
    ) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update(
        {"exp": expire}
    )

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# ==========================
# CURRENT USER
# ==========================

async def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = await users_collection.find_one(
        {
            "_id": ObjectId(user_id)
        }
    )

    if user is None:
        raise credentials_exception

    return user


# ==========================
# REGISTER
# ==========================

async def register_user(
    email: str,
    password: str
):

    existing_user = await users_collection.find_one(
        {"email": email}
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    user = {
        "email": email,
        "hashed_password": hash_password(password)
    }

    result = await users_collection.insert_one(
        user
    )

    return str(result.inserted_id)


# ==========================
# LOGIN
# ==========================

async def login_user(
    email: str,
    password: str
):

    user = await users_collection.find_one(
        {"email": email}
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(
        password,
        user["hashed_password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token(
        {
            "sub": str(user["_id"])
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }