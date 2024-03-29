import json
from flask import jsonify
from flask import request, Flask
from werkzeug.security import check_password_hash, generate_password_hash
from flask import request
import requests
from dotenv import load_dotenv
import os
import jwt
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
        "filter": {"_id": {"$oid": user_id}}
    })
    r = requests.post(action, headers=header, data=payload)

    if r.status_code != 200:
        # Log the error message for debugging
        error_message = r.text 
        app.logger.info(f"Error: {error_message}")

        return None

    result = json.loads(r.text).get('document', None)
    if result:
        return result.get('email', None)  # Ensure this matches the document's field name
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
    try:
        flag = request.cookies.get('flag')
    except:
        flag = None
    app.logger.warning(session_id)
    # Check if the session_id cookie was found
    if session_id is None:
        return jsonify({"error": "Session ID not found in cookies"}), 404
    else:
        # If the session_id cookie is not found, handle the absence accordingly
        pass
    # response = requests.post(auth_service_url,cookies={'session_id': session_id})
    if flag is not None:
        response = requests.post(AUTHO_SERVER_URL+"validate-session",json={'session_id': session_id,'flag':flag})
        if response.status_code == 200:
            response = response.json()
            app.logger.info(f"Response from autho: {response}")
            user_id = response['user_id']
            try:
                email = find_user_email_by_id(user_id)
                app.logger.info(f"Email: {email}")
            except:
                return jsonify({"info": "Cannot find user's email"}), 403
            # The authorization service confirms the session is valid
            return jsonify({"info": "User have logged in","email":email}), 200
        else:
            # If the document or access_token doesn't exist, or the session has expired, return False
            return jsonify({"info": "User not yet logged in"}), 403
    else:
        response = requests.post(AUTHO_SERVER_URL+"validate-session",json={'session_id': session_id})
        if response.status_code == 200:
            # The authorization service confirms the session is valid
            return jsonify({"info": "User have logged in"}), 200
        else:
            # If the document or access_token doesn't exist, or the session has expired, return False
            return jsonify({"info": "User not yet logged in"}), 403
    
    
    
@app.route('/api-authen/delete-session',methods=['POST'])
def delete_session():
    # Extract the session_id cookie from the incoming request
    session_id = request.cookies.get('session_id')
    app.logger.warning(session_id)
    # Check if the session_id cookie was found
    if session_id is None:
        return jsonify({"error": "Session ID not found in cookies"}), 404
    else:
        # If the session_id cookie is not found, handle the absence accordingly
        pass

    # auth_service_url = AUTHO_SERVER_URL+"validate-session"
    # app.logger.warning(auth_service_url)
    # response = requests.post(auth_service_url,cookies={'session_id': session_id})
    response = requests.post(AUTHO_SERVER_URL+"delete-session",json={'session_id': session_id})
    
    if response.status_code == 200:
        # The authorization service confirms the session is valid
        return jsonify({"info": "Logging out"}), 200
    else:
        # If the document or access_token doesn't exist, or the session has expired, return False
        return jsonify({"info": "User not yet logged in"}), 403
    
@app.route('/api-authen/signup', methods=['POST'])
def signup():

    try:
        json_req = request.get_json()
    except Exception as ex:
        return jsonify(info='Request Body incorrect json format: ' + str(ex)),442

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
        return jsonify(data=is_not_validate, info='Invalid parameters')

    email = json_body.get('email')
    password = json_body.get('password')
    password_hash = generate_password_hash(password)


    if isDuplicate(email):
        return jsonify(info="User Already Existed"),442
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
        return jsonify(info="Signup Success"),200


@app.route('/api-authen/login', methods=['POST'])
def login():
    try:
        json_req = request.get_json()
    except Exception as ex:
        return jsonify(info='Request Body incorrect json format: ' + str(ex)), 442
    
    # trim input body
    json_body = {}
    for key, value in json_req.items():
        json_body.setdefault(key, str(value).strip())

    # Validate request body
    is_not_validate = LoginBodyValidation().validate(json_body)  # Dictionary show detail error fields
    if is_not_validate:
        return jsonify(data=is_not_validate, info='Invalid params')

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
        return jsonify(info="User not existed"),442
    else:
        if(not check_password_hash(pwhash=result['password'],password=password)):
            return jsonify(info="Password Incorrect"),403
        else:
            #User is validated[]

            token = generate_token(result['_id'])
            try:
                response = requests.post(
                AUTHO_SERVER_URL+"authorize",
                headers={'Authorization': f'{token}'},json={"email":email}
                )
                if response.status_code !=200:
                    raise Exception
                
                response=response.json()
                session_id = response['session_id']

            except Exception as error:
                return jsonify({"info": f"Error {error}"}), 500
            return jsonify({"info":"Success", "session_id":session_id}), 200   

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5012,debug=True)