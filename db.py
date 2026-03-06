import os
from motor import motor_asyncio

DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://mongo_admin:password@db:27017")

client = motor_asyncio.AsyncIOMotorClient(DATABASE_URL)


async def get_db():
    return client
