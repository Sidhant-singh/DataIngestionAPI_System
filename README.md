# 📊 Data Ingestion API System

## 🔧 Tech Stack
- FastAPI
- Python 3.9+
- threading & asyncio
- In-memory storage (dictionary + queue)

## 📦 Features
- Submit ingestion jobs with priority
- Async batch processing (3 per batch, 1 batch per 5 seconds)
- View status with `GET /status/<ingestion_id>`

## 🚀 How to Run

```bash
git clone https://github.com/Sidhant-singh/DataIngestionAPI_System
cd data_ingestion_api
python -m venv ingestion && ingestion/Scripts/activate 
pip install -r requirements.txt
./run.sh
