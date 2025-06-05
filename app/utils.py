import uuid
import time

def generate_id():
    return str(uuid.uuid4())

def get_priority_value(priority: str):
    return {"HIGH": 1, "MEDIUM": 2, "LOW": 3}[priority]
