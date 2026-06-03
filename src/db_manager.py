from pymongo import MongoClient
from src.config import Config

class DBManager:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client.get_database("meditrack_db")

        self.users = self.db.users
        self.prescriptions = self.db.prescriptions
        self.chats = self.db.chats