from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with your React frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the users router
app.include_router(users.router, prefix="/api", tags=["api"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Big Data Optimizer API"}