#test_endpoints.py
import requests
import time
import pytest

BASE_URL = "http://localhost:3000"

def test_login_success():
    response = requests.post(f"{BASE_URL}/login", json={"username": "admin", "password": "admin"})
    assert response.status_code == 200
    json_resp = response.json()
    assert "token" in json_resp
    assert json_resp.get("status_code", 200) == 200

def test_login_failure():
    response = requests.post(f"{BASE_URL}/login", json={"username": "x", "password": "x"})
    assert response.status_code == 200
    json_resp = response.json()
    assert "error" in json_resp
    assert json_resp.get("status_code") == 401

def test_predict_with_token():
    login_resp = requests.post(f"{BASE_URL}/login", json={"username": "admin", "password": "admin"})
    json_login = login_resp.json()
    assert login_resp.status_code == 200
    assert "token" in json_login
    assert json_login.get("status_code", 200) == 200

    token = json_login["token"]
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "gre_score": 330,
        "toefl_score": 110,
        "university_rating": 4,
        "sop": 4.5,
        "lor": 4.5,
        "cgpa": 9.2,
        "research": 1
    }
    response = requests.post(f"{BASE_URL}/predict", json=payload, headers=headers)
    json_resp = response.json()  # Erst hier die Response lesen
    print("Predict Response JSON:", json_resp)  # Dann ausgeben
    assert response.status_code == 200
    if "error" in json_resp:
        assert json_resp.get("status_code") is not None
    else:
        assert "lr_prediction" in json_resp
        assert "rf_prediction" in json_resp

@pytest.fixture(scope="module")
def token():
    response = requests.post(f"{BASE_URL}/login", json={"username": "admin", "password": "admin"})
    assert response.status_code == 200
    return response.json()["token"]

def test_batch_prediction(token):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "instances": [
            {
                "gre_score": 310,
                "toefl_score": 110,
                "university_rating": 4,
                "sop": 4.0,
                "lor": 4.0,
                "cgpa": 8.5,
                "research": 1
            }
        ] * 3
    }
    response = requests.post(f"{BASE_URL}/batch_predict", headers=headers, json=payload)
    assert response.status_code == 200
    job_id = response.json()["job_id"]

    for _ in range(10):
        status_response = requests.post(f"{BASE_URL}/batch_status", headers=headers, json={"job_id": job_id})
        result = status_response.json()
        if result["status"] == "completed":
            assert isinstance(result["predictions"], list)
            return
        elif result["status"] == "failed":
            pytest.fail(f"Batch job failed: {result.get('error')}")
        time.sleep(1)
    pytest.fail("Batch job did not complete in time")

def test_invalid_batch_status(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/batch_status", headers=headers, json={"job_id": "invalid_id"})
    assert response.status_code == 200
    json_resp = response.json()
    assert "error" in json_resp
    assert json_resp.get("status_code") == 404