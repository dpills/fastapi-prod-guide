import asyncio
import hashlib
from datetime import datetime
from typing import Any, Generator

import pytest
from httpx import AsyncClient

from app.main import app
from app.utilities.db import db


async def add_db_test_user() -> None:
    """
    Add test user to Database
    """
    await db.tokens.update_one(
        {"user": "tester"},
        {
            "$set": {
                "access_token_hash": hashlib.sha256("GOOD_TOKEN".encode()).hexdigest(),
                "created_date": datetime.utcnow(),
            }
        },
        upsert=True,
    )

    return None


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, Any, None]:
    """
    Override Event Loop
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()

    # Add test user to DB
    loop.run_until_complete(add_db_test_user())

    yield loop
    loop.close()


@pytest.fixture()
def test_client() -> AsyncClient:
    """
    Create an instance of the client
    """
    return AsyncClient(app=app, base_url="http://test", follow_redirects=True)
