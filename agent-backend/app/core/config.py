import os
from dotenv import load_dotenv
import itertools
import threading
import random

load_dotenv()

_KEYS = os.getenv("GEMINI_KEYS", os.getenv("GOOGLE_API_KEY", "")).split(",")

_KEYS = [k.strip() for k in _KEYS if k.strip()]
if not _KEYS:
    raise EnvironmentError("Set GEMINI_KEYS to a comma-separated list of keys.")

GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")