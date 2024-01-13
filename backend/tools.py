import re

def extract_session_id(session_str: str):
    pattern = r'/sessions/([^/]+)/contexts/'
    match = re.search(pattern, session_str)
    if match:
        extracted = match.group(1)
        return extracted
    else:
        return ""
    
def get_string_from_food_dict(food_dict: dict):
    return ", ".join([f"{int(value)} {key}" for key, value in food_dict.items()])

def get_string_from_food_list(food_list: list):
    return ", ".join(food_list)
    
if __name__ == "__main__":
    # print(extract_session_id("projects/food-chatbot-lncb/agent/sessions/123-2bf6-d777-65f5-1b426cc4605c/contexts/ongoing-order"))
    # print(get_string_from_food_dict({"Nasi Goreng": "2", "Sate": "1"}))
    pass