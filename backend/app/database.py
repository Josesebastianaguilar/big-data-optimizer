from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI, DATABASE_NAME

client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

async def create_indexes():
    await db["records"].create_index("_id")
    await db["records"].create_index("repository")
    await db["records"].create_index("version")
    await db["repositories"].create_index("_id")
    await db["repositories"].create_index("data_ready")
    await db["repositories"].create_index("version")