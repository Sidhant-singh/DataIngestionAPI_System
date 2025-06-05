import time
import pytest
from fastapi.testclient import TestClient
from app.main import app  # Adjust if your app is located differently

client = TestClient(app)


def test_priority_order_and_rate_limit():
    print("\n--- Test: Priority Order & Rate Limiting ---")

    # Step 1: Send MEDIUM priority ingestion
    resp1 = client.post("/ingest", json={"ids": [1, 2, 3, 4, 5], "priority": "MEDIUM"})
    assert resp1.status_code == 200
    id1 = resp1.json()["ingestion_id"]
    print(f"Submitted MEDIUM priority ingestion_id: {id1}")

    # Step 2: Wait for 4 seconds and then send HIGH priority
    time.sleep(4)
    resp2 = client.post("/ingest", json={"ids": [6, 7, 8, 9], "priority": "HIGH"})
    assert resp2.status_code == 200
    id2 = resp2.json()["ingestion_id"]
    print(f"Submitted HIGH priority ingestion_id: {id2}")

    # Step 3: Wait for all batches to complete
    time.sleep(30)

    # Step 4: Check statuses
    res_high = client.get(f"/status/{id2}").json()
    res_med = client.get(f"/status/{id1}").json()

    assert res_high["status"] == "completed"
    assert res_med["status"] == "completed"

    high_batches = res_high["batches"]
    med_batches = res_med["batches"]

    print("HIGH priority batches:")
    for batch in high_batches:
        print(batch)

    print("MEDIUM priority batches:")
    for batch in med_batches:
        print(batch)

    # Verifying expected batches
    assert high_batches[0]["ids"] == [6, 7, 8]
    assert high_batches[1]["ids"] == [9]
    assert med_batches[0]["ids"] == [1, 2, 3]


def test_rate_limit_batch_processing():
    print("\n--- Test: Rate Limit Enforcement (1 batch per 5 seconds) ---")

    # Step 1: Send ingestion for 9 IDs (3 batches)
    response = client.post("/ingest", json={"ids": list(range(1, 10)), "priority": "MEDIUM"})
    assert response.status_code == 200
    ingestion_id = response.json()["ingestion_id"]
    print(f"Submitted ingestion_id: {ingestion_id}")

    # Step 2: Monitor batch completion every 5 seconds
    statuses = []
    for i in range(5):
        time.sleep(5)
        res = client.get(f"/status/{ingestion_id}")
        assert res.status_code == 200
        data = res.json()

        completed_batches = [b for b in data["batches"] if b["status"] == "completed"]
        statuses.append(len(completed_batches))
        print(f"[{(i+1)*5}s] Completed Batches: {len(completed_batches)}")

    # Step 3: Validate rate limiting behavior
    for i in range(1, len(statuses)):
        assert statuses[i] - statuses[i - 1] <= 1, "More than 1 batch processed in 5 seconds"

    assert statuses[-1] == 3, f"Expected 3 batches to complete, got {statuses[-1]}"
