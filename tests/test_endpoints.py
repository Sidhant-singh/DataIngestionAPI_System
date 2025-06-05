import pytest
from fastapi.testclient import TestClient
from app.main import app
import time

client = TestClient(app)

def test_priority_order_and_rate_limit():
    # Sending  MEDIUM priority
    resp1 = client.post("/ingest", json={"ids": [1, 2, 3, 4, 5], "priority": "MEDIUM"})
    id1 = resp1.json()["ingestion_id"]
    
    time.sleep(4)

    # Sending  HIGH priority
    resp2 = client.post("/ingest", json={"ids": [6, 7, 8, 9], "priority": "HIGH"})
    id2 = resp2.json()["ingestion_id"]

    time.sleep(30)

    # Checking HIGH priority completed before MEDIUM
    res_high = client.get(f"/status/{id2}").json()
    res_med = client.get(f"/status/{id1}").json()

    assert res_high["status"] == "completed"
    assert res_med["status"] == "completed"

    high_batches = [batch for batch in res_high["batches"]]
    med_batches = [batch for batch in res_med["batches"]]

    assert high_batches[0]["ids"] == [6, 7, 8]
    assert high_batches[1]["ids"] == [9]

    assert med_batches[0]["ids"] == [1, 2, 3]
