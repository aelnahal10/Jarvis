from fastapi import APIRouter, Request
from app.services.query_handler import process_query

router = APIRouter()

@router.post("/alexa/intent")
async def handle_intent(request: Request):
    data = await request.json()
    query = data.get("query", "")
    if not query:
        return {
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "I didn't get that, could you try again?"
                }
            }
        }

    # Send the query to the processor
    response = await process_query(query)
    return {
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": response
            }
        }
    }
