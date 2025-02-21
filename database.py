from pymongo import MongoClient
import config

client = MongoClient(config.MONGO_URI)
db = client.fitty_db
users_collection = db.users  # Collection for storing user details
