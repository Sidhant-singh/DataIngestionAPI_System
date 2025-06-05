# Data Ingestion API System

## Tech Stack
- FastAPI
- Python 3.9+
- threading & asyncio
- In-memory storage (dictionary + queue)

## Features
- Submit ingestion jobs with priority
- Async batch processing (3 per batch, 1 batch per 5 seconds)
- View status with `GET /status/<ingestion_id>`

## My Approach
1. API Design
Implemented two main endpoints using FastAPI:
POST /ingest → Accepts a list of IDs and a priority level.
GET /status/{ingestion_id} → Returns the current status of the ingestion job and its batches.

2. Batching & Priority Queue
IDs are split into batches of up to 3 IDs each.
Jobs are queued in a priority queue, where HIGH priority jobs are processed before MEDIUM, and MEDIUM before LOW.

3. Asynchronous Processing
A background worker runs in a loop and checks for pending jobs.
Each batch simulates ingestion with a delay (e.g., using asyncio.sleep()), and status is updated accordingly.

4. Status Tracking
Each ingestion job and batch has a unique ID and tracks its own status (triggered, completed).

5. Testing
Added unit tests for:
Ingestion request and job creation
Job status updates
Priority order enforcement

## How to Run

```bash
git clone https://github.com/Sidhant-singh/DataIngestionAPI_System
cd data_ingestion_api
python -m venv ingestion && ingestion/Scripts/activate 
pip install -r requirements.txt
./run.sh

