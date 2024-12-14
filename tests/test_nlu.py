from app.services.nlu import process_query

def test_process_query():
    query = "What is AI?"
    response = process_query(query)
    assert response == "Processing your query: What is AI?"
