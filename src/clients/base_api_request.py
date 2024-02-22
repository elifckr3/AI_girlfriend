import requests
from typing import Any


def push_request(api_key: str, url: str, headers: dict[str, str], data: dict[str, Any]):
    try:
        response = requests.post(url, headers=headers, json=data)

        return response

    except Exception as e:
        print(f"Error: {e}")
        return None
