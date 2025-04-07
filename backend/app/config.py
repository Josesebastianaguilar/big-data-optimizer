from dotenv import load_dotenv
import os

load_dotenv()

# Environment variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "big_data_optimizer")
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")  # Replace with a strong key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30