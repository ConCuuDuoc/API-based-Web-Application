import json
from flask import jsonify
from flask import request, Flask
from werkzeug.security import check_password_hash, generate_password_hash
from flask import request
import requests
from dotenv import load_dotenv
import os
import jwt
import jwcrypto.jwk as jwk
from datetime import datetime, timedelta
from validator import SignupBodyValidation, LoginBodyValidation
import requests


app = Flask(__name__)
#Secret key for sign cookie
load_dotenv() 
app.secret_key = os.getenv('SECRET_KEY')

# take environment variables from .env.
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


def isDuplicate(email : str):
    action = DB_ENDPOINT + "findOne"
    payload =json.dumps({
    "collection":"Data",
    "database":"Users",
    "dataSource":"ATM",
    "filter": {"email": email}
    })
    r = requests.post(action,headers=header,data=payload)
    result = json.loads(r.text)['document']
    if(result != None):
        return True
    else:
        return False

def find_user_email_by_id(user_id):
    action = DB_ENDPOINT + "findOne"
    payload = json.dumps({
        "collection": "Data",
        "database": "Users",
        "dataSource": "ATM",
        "filter": {"user_id": user_id}
    })
    r = requests.post(action, headers=header, data=payload)
    # It's important to handle potential errors in the response here
    if r.status_code != 200:
        # Handle error (e.g., log it, raise an exception, etc.)
        return None
    result = json.loads(r.text).get('document', None)
    if result:
        # Assuming 'email' is a field in your MongoDB document
        return result.get('email', None)
    else:
        return None

def generate_token(id : str, expiration_minutes: int = 15):
    expiration_time = datetime.utcnow() + timedelta(minutes=expiration_minutes)
    payload = {'id':id, 'exp':expiration_time}
    token = jwt.encode(
        payload=payload,
        key = SECRET_KEY,
        algorithm='ES256'
    )
    return token 

# Validate session (Check if user is logged in or not)

@app.route('/api-authen/validate-session',methods=['POST'])
def check_session():
    # Extract the session_id cookie from the incoming request
    session_id = request.cookies.get('session_id')
    # Check if the session_id cookie was found
    if session_id is None:
        return jsonify({"error": "Session ID not found in cookies"}), 404
    else:
        # If the session_id cookie is not found, handle the absence accordingly
        pass

    auth_service_url = AUTHO_SERVER_URL+"validate-session"
    response = requests.post(auth_service_url,cookies={'session_id': session_id})
    
    if response.status_code == 200:
        response.json()
        user_id = response['data']
        email = find_user_email_by_id(user_id)
        # The authorization service confirms the session is valid
        return jsonify({"message": "User have logged in","email":email}), 200
    else:
        # If the document or access_token doesn't exist, or the session has expired, return False
        return jsonify({"message": "User not yet logged in"}), 404
    
@app.route('/api-authen/signup', methods=['POST'])
def signup():

    try:
        json_req = request.get_json()
    except Exception as ex:
        return jsonify(message='Request Body incorrect json format: ' + str(ex)),442

    # Trim input body
    json_body = {}
    for key, value in json_req.items():
        if isinstance(value, str):
            json_body.setdefault(key, value.strip())
        else:
            json_body.setdefault(key, value)

    # Validate request body
    is_not_validate = SignupBodyValidation().validate(json_body)  # Dictionary show detail error fields
    if is_not_validate:
        return jsonify(data=is_not_validate, message='Invalid parameters')

    email = json_body.get('email')
    password = json_body.get('password')
    password_hash = generate_password_hash(password)


    if isDuplicate(email):
        return jsonify(data="User Already Existed"),442
    else:
        action = DB_ENDPOINT + "insertOne"
        payload =json.dumps({
        "collection":"Data",
        "database":"Users",
        "dataSource":"ATM",
        "document": {
            "email": email,
            "password":password_hash,    
            }
        })
        r = requests.post(action,headers=header,data=payload)
        print(r.text)
        return jsonify(data="Signup Success"),200


@app.route('/api-authen/login', methods=['POST'])
def login():
    try:
        json_req = request.get_json()
    except Exception as ex:
        return jsonify(message='Request Body incorrect json format: ' + str(ex)), 442
    
    # trim input body
    json_body = {}
    for key, value in json_req.items():
        json_body.setdefault(key, str(value).strip())

    # Validate request body
    is_not_validate = LoginBodyValidation().validate(json_body)  # Dictionary show detail error fields
    if is_not_validate:
        return jsonify(data=is_not_validate, message='Invalid params')

    #Check email and password
    email = json_body.get('email')
    password = json_body.get('password')

    action = DB_ENDPOINT + "findOne"
    payload =json.dumps({
    "collection":"Data",
    "database":"Users",
    "dataSource":"ATM",
    "filter": {"email": email}
    })

    r = requests.post(action,headers=header,data=payload)
    # print(r.text)
    result = json.loads(r.text)['document']
    
    if(result == None):
        return jsonify(data="User not existed"),442
    else:
        if(not check_password_hash(pwhash=result['password'],password=password)):
            return jsonify(data="Password Incorrect"),403
        else:
            #User is validated[]

            token = generate_token(result['_id'])
            try:
                response = requests.post(
                AUTHO_SERVER_URL+"authorize",
                headers={'Authorization': f'{token}'}
                )
                if response.status_code !=200:
                    raise Exception
                
                response=response.json()
                session_id = response['session_id']

            except Exception as error:
                return jsonify({"error": f"Error login: {error}"}), 500
            return jsonify(data="Login Success", session_id=session_id), 200   

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5012)