import os
from passlib.context import CryptContext
from app.database import db
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Predefined users
USERS = [
    {"username": "admin", "role": "admin", "password": os.getenv("ADMIN_PASSWORD")},
    {"username": "user", "role": "user", "password": os.getenv("USER_PASSWORD")},
]

async def create_users():
    for user in USERS:
        # Check if the user already exists
        existing_users = await db["users"].find()
        if existing_user.len():
            print(f"Users already exist. Skipping...")
            continue

        # Hash the password and insert the user into the database
        hashed_password = pwd_context.hash(user["password"])
        new_user = {"username": user["username"], "hashed_password": hashed_password}
        await db["users"].insert_one(new_user)
        print(f"User '{user['username']}' created successfully.")

# Entry point for the script
if __name__ == "__main__":
    import asyncio
    asyncio.run(create_users())