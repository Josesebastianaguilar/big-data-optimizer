from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI, DATABASE_NAME
import logging
import asyncio

index_lock = asyncio.Lock()
client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

async def create_indexes():
    try:
        logging.info("Creating indexes for collections...")
        await db["records"].create_index("_id")
        await db["records"].create_index("repository")
        await db["records"].create_index("version")
        await db["repositories"].create_index("_id")
        await db["repositories"].create_index("data_ready")
        await db["repositories"].create_index("version")
        await db["processes"].create_index("_id")
        await db["processes"].create_index("repository")
        await db["processes"].create_index("trigger_type")
        await db["processes"].create_index("process_id")
        await db["processes"].create_index("repository_version")
        await db["processes"].create_index("iteration")
        await db["processes"].create_index("validated")
        await db["processes"].create_index("status")
        await db["jobs"].create_index("_id")
        await db["process_results"].create_index("_id")
        await db["process_results"].create_index("batch_number")
        await db["process_results"].create_index("process_id")
        await db["process_results"].create_index("process_item_id")
        logging.info("Indexes created successfully.")
        
    except Exception as e:
        logging.error(f"Error creating indexes: {str(e)}")
        raise e
        