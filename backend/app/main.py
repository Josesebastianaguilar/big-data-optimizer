from app.logging_config import *
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, repositories, records, processes
from app.cron.cron_jobs import start_cron_jobs, stop_cron_jobs
from app.database import create_indexes
from dotenv import load_dotenv
import os

load_dotenv()
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],  # Replace with your React frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the users router
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(repositories.router, prefix="/api/repositories", tags=["repositories"])
app.include_router(records.router, prefix="/api/records", tags=["records"])
app.include_router(processes.router, prefix="/api/processes", tags=["processes"])

# Start cron jobs when the application starts
@app.on_event("startup")
async def startup_event():
    start_cron_jobs()
    await create_indexes()

# Stop cron jobs when the application shuts down
@app.on_event("shutdown")
async def shutdown_event():
    stop_cron_jobs()