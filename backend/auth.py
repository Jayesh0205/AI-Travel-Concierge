
import logging
import os

import httpx
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from database.pg_database import SessionLocal
from database.pg_models import User

load_dotenv(override=True)

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY", "")

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> User:
    """Verify Supabase authentication and link the PostgreSQL user."""

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Please sign in to continue.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not SUPABASE_URL or not SUPABASE_PUBLISHABLE_KEY:
        logger.error("Supabase authentication configuration is missing.")
        raise HTTPException(
            status_code=503,
            detail="Authentication service is not configured.",
        )

    token = credentials.credentials

    # Verify the access token with Supabase Auth.
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": SUPABASE_PUBLISHABLE_KEY,
                },
            )
    except httpx.RequestError:
        logger.exception("Could not connect to Supabase Auth.")
        raise HTTPException(
            status_code=503,
            detail="Authentication service is temporarily unavailable.",
        )

    if response.status_code in (401, 403):
        raise HTTPException(
            status_code=401,
            detail="Your session is invalid or expired. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if response.status_code != 200:
        logger.error("Supabase Auth returned HTTP %s.", response.status_code)
        raise HTTPException(
            status_code=503,
            detail="Could not verify your login. Please try again.",
        )

    # Read verified account information.
    try:
        auth_data = response.json()

        auth_user_id = auth_data.get("id")
        email = (auth_data.get("email") or "").strip().lower()
        email_confirmed = bool(auth_data.get("email_confirmed_at"))

        metadata = auth_data.get("user_metadata") or {}
        full_name = metadata.get("full_name")

        if isinstance(full_name, str):
            full_name = full_name.strip() or None
        else:
            full_name = None

        if not auth_user_id or not email:
            raise ValueError("Supabase user ID or email is missing.")

    except (ValueError, TypeError):
        logger.exception("Invalid Supabase user information.")
        raise HTTPException(
            status_code=401,
            detail="Invalid account information. Please sign in again.",
        )

    try:
        with SessionLocal() as session:

            # First: find an account already linked to this Supabase user.
            user = session.scalar(
                select(User).where(User.auth_user_id == auth_user_id)
            )

            if user is not None:
                if user.email.lower() != email:
                    user.email = email

                if not user.full_name and full_name:
                    user.full_name = full_name

            else:
                # Second: find an existing account by verified email.
                user = session.scalar(
                    select(User).where(User.email == email)
                )

                if user is not None:
                    if not email_confirmed:
                        raise HTTPException(
                            status_code=403,
                            detail="Verify your email before linking your account.",
                        )

                    if user.auth_user_id and user.auth_user_id != auth_user_id:
                        raise HTTPException(
                            status_code=403,
                            detail="This account is already linked to another login.",
                        )

                    user.auth_user_id = auth_user_id

                    if not user.full_name and full_name:
                        user.full_name = full_name

                else:
                    # Third: create a new verified application account.
                    if not email_confirmed:
                        raise HTTPException(
                            status_code=403,
                            detail="Please verify your email before continuing.",
                        )

                    base_username = email.split("@")[0][:80] or "traveler"
                    username = base_username
                    suffix = 1

                    while session.scalar(
                        select(User.id).where(User.username == username)
                    ):
                        username = f"{base_username[:90]}_{suffix}"
                        suffix += 1

                    user = User(
                        username=username,
                        email=email,
                        full_name=full_name,
                        auth_user_id=auth_user_id,
                        role="user",
                    )

                    session.add(user)

                session.commit()
            session.refresh(user)

            return user

    except HTTPException:
        raise

    except IntegrityError:
        logger.exception("PostgreSQL account linking conflict.")
        raise HTTPException(
            status_code=409,
            detail="Could not link your account. Please try again.",
        )

    except Exception:
        logger.exception("Failed to load authenticated PostgreSQL user.")
        raise HTTPException(
            status_code=503,
            detail="Could not load your account. Please try again.",
        )


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Allow access only to users with the admin role."""

    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required.",
        )

    return current_user
