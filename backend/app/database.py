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
        await db["processes"].create_index("parameters")
        await db["processes"].create_index("created_at")
        await db["processes"].create_index("updated_at")
        await db["processes"].create_index("valid")
        await db["processes"].create_index("optimized")
        await db["processes"].create_index("task_process")
        await db["processes"].create_index("duration")
        await db["processes"].create_index("results.group")
        await db["processes"].create_index("results.values")
        await db["jobs"].create_index("_id")
        await db["jobs"].create_index("type")
        await db["jobs"].create_index("data")
        logging.info("Indexes created successfully.")
    except Exception as e:
        logging.error(f"Error creating indexes: {str(e)}")
        raise e
    
async def recreate_records_indexes_from_repositories():
    async with index_lock:
        try:
            logging.info("Recreating indexes for records based on repositories parameters...")
            indexes = await db["records"].list_indexes().to_list(length=None)
            
            for idx in indexes:
                if idx["name"] != "_id_":
                    await db["records"].drop_index(idx["name"])

            repositories = await db["repositories"].find({}, {"parameters": 1}).to_list(length=None)
            parameter_names = set()
            for repo in repositories:
                params = repo.get("parameters", [])
                for p in params:
                    parameter_names.add(p["name"])
            
            for param in parameter_names:
                await db["records"].create_index(f"data.{param}")

            await db["records"].create_index("_id")
            await db["records"].create_index("repository")
            await db["records"].create_index("version")
            
            logging.info("Indexes for records recreated successfully.")
        except Exception as e:
            logging.error(f"Error recreating indexes for records: {str(e)}")
            raise e