from motor.motor_asyncio import AsyncIOMotorClient
from typing import List
from app.models.schemas import Location
from app.core.config import MONGO_URI

client = AsyncIOMotorClient(MONGO_URI)
db = client["trip_planner_db"]

async def save_verified_locations(locations: List[Location]) -> None:
    collection = db["verified_locations"]
    data = [{"address": loc.address, "lat": loc.lat, "lng": loc.lng} for loc in locations]
    await collection.insert_many(data)
