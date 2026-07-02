from datetime import datetime
import requests
from utils.logger import *
from utils.globals import GEKOKUAI_VERSION

def return_response(result: bool, description: str, **kwargs):
    response = {
        "result": result,
        "description": description
    }
    response.update(kwargs)
    return response

def parse_response(response):
    verbose(response)
    print(f"[{datetime.now()}]")
    print(f"GekokuAI {GEKOKUAI_VERSION}\n")
    if response.status_code == 200:
        parsed_data = response.json()
        for key, value in parsed_data.items():
            formatted_key = key.replace("_", " ")
            print(f"{formatted_key.capitalize():<15} | {value}")
    else:
        print(f"Daemon responded with status {response.status_code}")
        try:
            parsed_data = response.json()
            for key, value in parsed_data.items():
                print(f"{key.capitalize():<15} | {value}")
        except requests.exceptions.JSONDecodeError:
            print(f"Raw Response    | {response.text.strip()}")