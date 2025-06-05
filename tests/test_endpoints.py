# import pytest
# from fastapi.testclient import TestClient
# from app.main import app
# import time

# client = TestClient(app)

# def test_priority_order_and_rate_limit():
#     # Sending  MEDIUM priority
#     resp1 = client.post("/ingest", json={"ids": [1, 2, 3, 4, 5], "priority": "MEDIUM"})
#     id1 = resp1.json()["ingestion_id"]
    
#     time.sleep(4)

#     # Sending  HIGH priority
#     resp2 = client.post("/ingest", json={"ids": [6, 7, 8, 9], "priority": "HIGH"})
#     id2 = resp2.json()["ingestion_id"]

#     time.sleep(30)

#     # Checking HIGH priority completed before MEDIUM
#     res_high = client.get(f"/status/{id2}").json()
#     res_med = client.get(f"/status/{id1}").json()

#     assert res_high["status"] == "completed"
#     assert res_med["status"] == "completed"

#     high_batches = [batch for batch in res_high["batches"]]
#     med_batches = [batch for batch in res_med["batches"]]

#     assert high_batches[0]["ids"] == [6, 7, 8]
#     assert high_batches[1]["ids"] == [9]

#     assert med_batches[0]["ids"] == [1, 2, 3]

# Another testcase to ensure rate limiting works correctly with batch processing
import time
import pytest
from fastapi.testclient import TestClient
from app.main import app  

client = TestClient(app)

def test_rate_limit_batch_processing():
    response = client.post("/ingest", json={"ids": list(range(1, 10)), "priority": "MEDIUM"})
    assert response.status_code == 200
    ingestion_id = response.json()["ingestion_id"]
    assert ingestion_id is not None

    statuses = []
    timestamps = []

    for i in range(5):  
        time.sleep(5)
        res = client.get(f"/status/{ingestion_id}")
        assert res.status_code == 200
        data = res.json()

        completed_batches = [b for b in data["batches"] if b["status"] == "completed"]
        statuses.append(len(completed_batches))
        timestamps.append(time.time())
        print(f"[{i*5}s] Completed: {len(completed_batches)}")

    for i in range(1, len(statuses)):
        assert statuses[i] - statuses[i - 1] <= 1, "More than 1 batch processed in 5 seconds"

    assert statuses[-1] == 3, f"Expected 3 batches to complete, but got {statuses[-1]}"
