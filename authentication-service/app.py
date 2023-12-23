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
load_dotenv()  # take environment variables from .env.
AUTH_SERVER_URL = "http://192.168.1.10:5013/authorize"
secret_key = os.getenv('SECRET_KEY')

# Init MongoDB ============================
mongodb_api = os.getenv('API_KEY')
db_endpoint = os.getenv('DB_ENDPOINT')
header = {
    'Content-Type': 'application/json',
    'Access-Control-Request-Headers':'*',
    'api-key':mongodb_api
}
# =========================================


def isDuplicate(email : str):
    action = db_endpoint + "findOne"
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

def generate_token(id : str, expiration_minutes: int = 20):
    expiration_time = datetime.utcnow() + timedelta(minutes=expiration_minutes)
    payload = {'id':id, 'exp':expiration_time}
    token = jwt.encode(
        payload=payload,
        key = secret_key,
        algorithm='HS256'
    )
    return token.decode()    
 
     
@app.route('/signup', methods=['POST'])
def signup():

    try:
        json_req = request.get_json()
    except Exception as ex:
        return jsonify(message='Request Body incorrect json format: ' + str(ex), code=442)

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
        return jsonify(data="User Already Existed",code=442)
    else:
        action = db_endpoint + "insertOne"
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
        return jsonify(data="Signup Success",code=200)


@app.route('/login', methods=['POST'])
def login():
    try:
        json_req = request.get_json()
    except Exception as ex:
        return jsonify(message='Request Body incorrect json format: ' + str(ex), code=442)
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

    action = db_endpoint + "findOne"
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
        return jsonify(data="User not existed",code=442)
    else:
        if(not check_password_hash(pwhash=result['password'],password=password)):
            return jsonify(data="Password Incorrect",code=403)
        else:
            token = generate_token(result['_id'])
            auth_server_response = requests.post(
                AUTH_SERVER_URL,
                headers={'Authorization': f'{token}'}
            )
            print(token)
            return jsonify(data="Login Success", message=token, code=200)       

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5012,debug=True)
    print(secret_key)