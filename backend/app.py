from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import db_helper
from tools import extract_session_id, get_string_from_food_dict, get_string_from_food_list

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
        "order_remove - context: ongoing-order": remove_from_order
    }

    return intent_handler_dict[intent](parameters, session_id)

def remove_from_order(parameters: dict, session_id: str):
    if session_id not in inprogress_order:
        fulfillment_text = "I apologize, but it seems we're unable to locate your current order. Could you please place a new order?"
    else:
        current_order = inprogress_order[session_id]
        food_items = parameters["food-item"]

        removed_items = []
        no_such_item = []

        for item in food_items:
            if item not in current_order:
                no_such_item.append(item)
            else:
                removed_items.append(item)
                del current_order[item]
        
        fulfillment_text = ""
        if len(removed_items) > 0:
            fulfillment_text += f"We have successfully removed {get_string_from_food_list(removed_items)} from your order. "

        if len(no_such_item) > 0:
            fulfillment_text += f"Unfortunately, we couldn't find {get_string_from_food_list(no_such_item)} in your current order. "

        if len(current_order.keys()) == 0:
            fulfillment_text += "Your order is now empty."
        else:
            fulfillment_text += f"Your updated order includes {get_string_from_food_dict(current_order)}."

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def complete_order(parameters: dict, session_id: str):
    if session_id not in inprogress_order:
        fulfillment_text = "Sorry, it seems like you haven't added anything to your order yet. Would you like to place a new order?"
    else:
        order = inprogress_order[session_id]
        if order == {}:
            return JSONResponse(
            content={"fulfillmentText": "Sorry, it seems like you haven't added anything to your order yet. Would you like to place an order?"}
        )
        order_id = save_to_db(order)
        total_price = db_helper.get_total_price(order_id)
        if order_id == -1:
            fulfillment_text = "I'm sorry, but we encountered an issue while processing your order. Please try again later or contact customer support for assistance."
        else:
            fulfillment_text = f"Thank you for choosing our service! Your order (ID: {order_id}) has been successfully placed. " \
                               f"Your total payment is: ${total_price:.2f}. " \
                               f"We appreciate your business and look forward to serving you again!"
    
    # Clear the in-progress order for the session
    del inprogress_order[session_id]

    return JSONResponse(
        content={"fulfillmentText": fulfillment_text}
    )

def save_to_db(order: dict):
    next_order_id = db_helper.get_next_avaliable_order_id()

    for food_item, food_quantity in order.items():
        rcode = db_helper.insert_order_item(food_item, int(food_quantity), next_order_id)

        if rcode == -1:
            return -1
    
    db_helper.insert_order_tracking(next_order_id, "in progress")
    
    return next_order_id


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
        fulfillment_text = f"Got it! These are your current order: {order_str}. Is there anything else you'd like to add or modify in your order?"
    # print(inprogress_order)
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
