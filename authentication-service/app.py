import json
from flask import jsonify
from flask import request, Flask, session
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
app.secret_key = os.getenv('SECRET_KEY')

load_dotenv()  # take environment variables from .env.
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

def generate_token(id : str, expiration_minutes: int = 15):
    expiration_time = datetime.utcnow() + timedelta(minutes=expiration_minutes)
    payload = {'id':id, 'exp':expiration_time}
    token = jwt.encode(
        payload=payload,
        key = SECRET_KEY,
        algorithm='ES256'
    )
    return token 
 
     
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
                requests.post(
                AUTHO_SERVER_URL,
                headers={'Authorization': f'{token}'}
                )
            except Exception as error:
                return jsonify({"error": f"Error login: {error}"}), 500
            return jsonify(data="Login Success", message=token), 200   

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5012,debug=True)