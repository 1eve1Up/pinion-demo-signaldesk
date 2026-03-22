from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from signaldesk.db.session import get_async_session
from signaldesk.models import User
from signaldesk.schemas.auth import TokenResponse, UserLogin, UserRegister
from signaldesk.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    body: UserRegister,
    session: AsyncSession = Depends(get_async_session),
) -> TokenResponse:
    existing = await session.execute(select(User).where(User.email == str(body.email)))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    user = User(
        email=str(body.email).lower(),
        hashed_password=hash_password(body.password),
    )
    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        ) from None
    await session.refresh(user)
    access_token = create_access_token(str(user.id))
    return TokenResponse(access_token=access_token)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: UserLogin,
    session: AsyncSession = Depends(get_async_session),
) -> TokenResponse:
    result = await session.execute(select(User).where(User.email == str(body.email).lower()))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    access_token = create_access_token(str(user.id))
    return TokenResponse(access_token=access_token)
