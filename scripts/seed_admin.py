#!/usr/bin/env python3
"""
Seed the initial admin user.
Usage:
    cd backend
    python ../scripts/seed_admin.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from core.database import AsyncSessionFactory
from core.security import hash_password
from repositories.user_repo import UserRepository


ADMIN_EMAIL = "admin@platform.local"
ADMIN_PASSWORD = "Admin@1234"


async def seed():
    async with AsyncSessionFactory() as db:
        repo = UserRepository(db)
        existing = await repo.get_by_email(ADMIN_EMAIL)
        if existing:
            print(f"Admin already exists: {ADMIN_EMAIL}")
            return

        user = await repo.create(
            email=ADMIN_EMAIL,
            password_hash=hash_password(ADMIN_PASSWORD),
            role="admin",
        )
        await db.commit()
        print(f"[SUCCESS] Admin user created: {ADMIN_EMAIL}")
        print(f"   Password: {ADMIN_PASSWORD}")
        print(f"   ID: {user.id}")


if __name__ == "__main__":
    asyncio.run(seed())
