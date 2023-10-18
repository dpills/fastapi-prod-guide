import hashlib
from datetime import datetime
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.utilities.db import db

from .models import OauthException, OauthToken

router = APIRouter()
security = HTTPBearer()


@router.get(
    "/callback",
    response_model=OauthToken,
    responses={
        400: {"description": "Oauth Error", "model": OauthException},
    },
)
async def oauth_callback(
    code: str = Query(description="Authorization Code"),
) -> OauthToken:
    """
    GitHub Oauth Integration Callback
    """
    async with httpx.AsyncClient() as client:
        token_result = await client.post(
            "https://github.com/login/oauth/access_token",
            json={
                "client_id": settings.github_oauth_client_id,
                "client_secret": settings.github_oauth_client_secret,
                "code": code,
                "redirect_uri": "http://localhost:8000/v1/auth/callback",
            },
            headers={"Accept": "application/json"},
        )
        data = token_result.json()
        error = data.get("error")
        if error:
            raise HTTPException(
                status_code=400,
                detail=f"{data.get('error')}: {data.get('error_description')}",
            )

        access_token: str = data.get("access_token")
        user_result = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_data = user_result.json()
        user = user_data.get("login")

    await db.tokens.insert_one(
        {
            "user": user,
            "access_token_hash": hashlib.sha256(access_token.encode()).hexdigest(),
            "created_date": datetime.utcnow(),
        },
    )

    return OauthToken(access_token=access_token)


async def validate_access_token(
    access_token: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> str:
    """
    Validate an access token
    Returns the username or raises a 401 HTTPException
    """
    access_token_hash = hashlib.sha256(access_token.credentials.encode()).hexdigest()
    cached_token = await db.tokens.find_one({"access_token_hash": access_token_hash})

    if cached_token:
        user: str | None = cached_token.get("user")
        if user:
            return user

    async with httpx.AsyncClient() as client:
        user_result = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token.credentials}"},
        )

        if user_result.status_code == 200:
            user_data = user_result.json()
            user = user_data.get("login")
            if user:
                await db.tokens.insert_one(
                    {
                        "user": user,
                        "access_token_hash": access_token_hash,
                        "created_date": datetime.utcnow(),
                    },
                )
                return user

    raise HTTPException(
        status_code=401,
        detail="Unauthorized",
    )
