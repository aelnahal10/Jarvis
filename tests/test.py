from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_alexa_request():
    data = {
        "request": {
            "type": "IntentRequest",
            "intent": {
                "name": "GeneralQueryIntent",
                "slots": {
                    "query": {"value": "What is the weather?"}
                }
            }
        }
    }
    response = client.post("/alexa", json=data)
    assert response.status_code == 200
    assert "Processing your query" in response.json()["response"]["outputSpeech"]["text"]
