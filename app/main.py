from fastapi import FastAPI, HTTPException
from app.models import IngestRequest, BatchInfo, BatchStatus
from app.utils import generate_id
from app.processor import start_background_worker
from app.storage import ingestion_store, priority_queue, storage_lock
import time

app = FastAPI()

start_background_worker()

@app.post("/ingest")
def ingest(request: IngestRequest):
    ingestion_id = generate_id()
    batches = []

    ids = request.ids
    for i in range(0, len(ids), 3):
        batch_ids = ids[i:i + 3]
        batch_id = generate_id()
        batch = {
            "batch_id": batch_id,
            "ids": batch_ids,
            "status": BatchStatus.YET_TO_START
        }
        batches.append(batch)
        with storage_lock:
            priority_queue.append((request.priority, time.time(), ingestion_id, batch))

    with storage_lock:
        ingestion_store[ingestion_id] = {
            "priority": request.priority,
            "batches": batches
        }

    return {"ingestion_id": ingestion_id}

@app.get("/status/{ingestion_id}")
def status(ingestion_id: str):
    with storage_lock:
        if ingestion_id not in ingestion_store:
            raise HTTPException(status_code=404, detail="Ingestion ID not found")

        data = ingestion_store[ingestion_id]
        batch_statuses = [b['status'] for b in data['batches']]

        if all(s == BatchStatus.YET_TO_START for s in batch_statuses):
            overall = "yet_to_start"
        elif all(s == BatchStatus.COMPLETED for s in batch_statuses):
            overall = "completed"
        else:
            overall = "triggered"

        return {
            "ingestion_id": ingestion_id,
            "status": overall,
            "batches": data["batches"]
        }
