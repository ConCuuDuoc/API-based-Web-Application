from dotenv import load_dotenv
from flask import Blueprint
from bson.objectid import ObjectId
import os
import json
import requests


load_dotenv()  # take environment variables from .env.

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
    "collection":"Data",
    "database":"Users",
    "dataSource":"ATM",
    "filter": {"_id": {"$oid": user_id}}, 
    })

    r = requests.post(action,headers=header,data=payload)
    result = json.loads(r.text).get('document')
    if(result != None):
        return True
    else:
        return False


