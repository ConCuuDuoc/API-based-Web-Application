from dotenv import load_dotenv
from flask import Blueprint
import os
import json
import requests

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)  # take environment variables from .env.

mongodb_api = os.getenv('API_KEY')
api = Blueprint('author', __name__)
db_endpoint = os.getenv('DB_ENDPOINT')
header = {
    'Content-Type': 'application/json',
    'Access-Control-Request-Headers':'*',
    'api-key':mongodb_api
}

def find_user(user_id: str):
    action = db_endpoint + "findOne"
    payload =json.dumps({
        "collection": "Auth",
        "database": "Auth",
        "dataSource": "Cluster0",
        "filter": {"uid": user_id},
    })
    r = requests.post(action,headers=header,data=payload)
    result = json.loads(r.text).get('document')
    if(result != None):
        return True
    else:
        return False

def add_user(user_id: str,role: str, scopes: list ):
    action = db_endpoint + "insertOne"
    payload =json.dumps({
        "collection": "Auth",
        "database": "Auth",
        "dataSource": "Cluster0",
        "document": {"uid": user_id,
                    "role": role, 
                    "scopes": scopes}
    })
    r = requests.post(action,headers=header,data=payload)
    print(r.text)
    return None

def get_user_role_scope(user_id: str):
    # Build the findOne API URL
    url = db_endpoint + "findOne"

    # Prepare the payload with collection, database, filter, and dataSource
    payload = {
        "collection": "Auth",
        "database": "Auth",
        "dataSource": "Cluster0",
        "filter": {"uid": user_id},
    }

    try:
        # Send POST request with headers and payload
        response = requests.post(url, headers=header, json=payload)

        # Raise exception if request fails
        response.raise_for_status()

    except requests.exceptions.RequestException as error:
        raise ValueError(f"Error retrieving user information: {error}")

    # Parse the JSON response
    data = response.json()

    # Check if document exists
    document = data.get("document")
    if not document:
        return None, None

    # Extract user role and scopes from document
    try:
        user_role = document["role"]
        user_scopes = document["scopes"]
    except KeyError as error:
        raise ValueError(f"Missing required fields in user document: {error}")

    # Return user role and scopes
    return user_role, user_scopes