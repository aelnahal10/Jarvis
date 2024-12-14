from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/alexa")
async def handle_alexa_request(request: Request):
    body = await request.json()
    query = body.get("query", "")
    if not query:
        return {"response": "No query received."}

    # Process the query (placeholder for real NLU logic)
    processed_response = f"You asked about {query}. Here's a brief response."
    return {"response": processed_response}
