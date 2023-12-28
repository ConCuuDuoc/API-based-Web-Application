import json
import requests
import os
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv() 
AUTHO_SERVER_URL = os.getenv('AUTHO_SERVER')
SECRET_KEY = str(os.getenv('SECRET_KEY'))

# Init MongoDB ============================
MONGODB_API = os.getenv('API_KEY')
DB_ENDPOINT = os.getenv('DB_ENDPOINT')
header = {
    'Content-Type': 'application/json',
    'Access-Control-Request-Headers':'*',
    'api-key':MONGODB_API
}
# =========================================

def find_user_email_by_id(user_id):
    action = DB_ENDPOINT + "findOne"
    payload = json.dumps({
        "collection": "Data",
        "database": "Users",
        "dataSource": "ATM",
         "filter": {"_id": {"$oid": user_id}}
    })
    r = requests.post(action, headers=header, data=payload)

    if r.status_code != 200:
        # Log the error message for debugging
        error_message = r.text 
        print(f"Error: {error_message}")

        return None

    result = json.loads(r.text).get('document', None)
    if result:
        return result.get('email', None)  # Ensure this matches the document's field name
    else:
        return None

# Replace 'your_user_id' with the actual user ID you're querying for
user_id = '658683ade4826beb78333892'
email = find_user_email_by_id(user_id)
print(f"User email: {email}")
