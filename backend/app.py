from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import db_helper

app = FastAPI()

@app.post("/")
async def handle_request(request: Request):
    # Retrieve the JSON data from the request
    payload = await request.json()

    # Extract the necessary information from the payload
    # based on the structure of the WebhookRequest from Dialogflow
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']

    if intent == "track_order - context: ongoing-tracking":
        return track_order(parameters)

    
def track_order(parameters: dict):
    order_id = int(parameters['order_id'])
    order_status = db_helper.get_order_status(order_id)

    if order_status:
        fulfillment_text = f"Great news! Your order (ID: {order_id}) is currently {order_status.lower()}."
    else:
        fulfillment_text = f"We're sorry, but we couldn't find any information for order ID: {order_id}. " \
                           f"Please double-check the ID and try again, or contact our support for assistance."

    return JSONResponse(
        content={"fulfillmentText": fulfillment_text}
    )
