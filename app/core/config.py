# all configurations
import os
from dotenv import load_dotenv

load_dotenv()

class Config():
    PROJECT_NAME="Tick-It AI Backend"
    API_VI_STR="/api/v1"

    DATABASE_URL=os.getenv("DATABASE_URL")
    SECRET_KEY=os.getenv("SECRET_KEY")
    ALGORITHM=os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

config=Config()