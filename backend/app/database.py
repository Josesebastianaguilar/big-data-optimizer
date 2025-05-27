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
    await db["processes"].create_index("_id")
    await db["processes"].create_index("repository")
    await db["processes"].create_index("trigger_type")
    await db["processes"].create_index("process_id")
    await db["processes"].create_index("repository_version")
    await db["processes"].create_index("iteration")
    await db["processes"].create_index("validated")
    await db["processes"].create_index("valid")
    await db["processes"].create_index("optimized")
    await db["processes"].create_index("task_process")
    await db["processes"].create_index("duration")
    await db["processes"].create_index("results.group")
    await db["processes"].create_index("results.values")
    
async def recreate_records_indexes_from_repositories():
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