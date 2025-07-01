from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

if not all([BOT_TOKEN, MONGO_URI, DB_NAME]):
    raise ValueError("One or more environment variables are missing!")
