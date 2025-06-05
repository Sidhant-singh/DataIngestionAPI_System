from collections import defaultdict, deque
import threading

storage_lock = threading.Lock()
ingestion_store = {} # Dictionary to store ingestion data
# Dictionary to store batches with ingestion_id as key 
priority_queue = deque()   # Deque to store batches in priority order

