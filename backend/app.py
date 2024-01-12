from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import db_helper
from tools import extract_session_id, get_string_from_food_dict

app = FastAPI()
inprogress_order = {}

@app.post("/")
async def handle_request(request: Request):
    # Retrieve the JSON data from the request
    payload = await request.json()

    # Extract the necessary information from the payload
    # based on the structure of the WebhookRequest from Dialogflow
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']

    session_id = extract_session_id(output_contexts[0]['name'])

    intent_handler_dict = {
        "track_order - context: ongoing-tracking": track_order,
        "order_add - context: ongoing-order": add_to_order,
        "order_complete - context: ongoing-order": complete_order,
        # "order_remove - context: ongoing-order": remove_from_order
    }

    return intent_handler_dict[intent](parameters, session_id)

def complete_order(parameters: dict, session_id: str):
    if session_id not in inprogress_order:
        fulfillment_text = "Sorry, it seems like you haven't added anything to your order yet. Would you like to place an order?"
    else:
        order = inprogress_order[session_id]
        # save_to_db(order)

# def save_to_db(order):



def add_to_order(parameters: dict, session_id: str):
    food_items = parameters["food-item"]
    food_quantity = parameters["number"]

    if len(food_items) != len(food_quantity):
        fulfillment_text = "Sorry, we didn't quite catch that. Could you please specify both the food items and quantities? (e.g., 'Two portions of Nasi Goreng' or 'One serving of Satay')"
    else:
        new_food_dict = dict(zip(food_items, food_quantity))

        if session_id in inprogress_order:
            inprogress_order[session_id].update(new_food_dict)
        else:
            inprogress_order[session_id] = new_food_dict

        order_str = get_string_from_food_dict(inprogress_order[session_id])
        fulfillment_text = f"Got it! Adding {order_str} to your order. Is there anything else you'd like to add or modify in your order?"
    
    return JSONResponse(
        content={"fulfillmentText": fulfillment_text}
    )

def track_order(parameters: dict, session_id: str):
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
