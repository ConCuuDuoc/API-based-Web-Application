from flask import Flask, request, jsonify,  session,g
from db import get_user_role_scope, find_user, add_user
from pymongo import MongoClient
from datetime import datetime, timedelta
from dotenv import load_dotenv
from bson.objectid import ObjectId

import os
import base64
import jwt
import json

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)  # take environment variables from .env.

PUBLIC_KEY = str(os.getenv("PUBLIC_KEY"))
SECRET_KEY = str(os.getenv('SECRET_KEY'))

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

#Secret key for sign cookie
app.secret_key = SECRET_KEY

# Init MongoDB ============================
client = MongoClient(os.getenv("SESSION_HOST"), 27017)
db = client['SessionStorage']
session_collection = db['access-sessions']
# =========================================
# Set up for session=======================
def generate_session_id():
    return base64.b64encode(os.urandom(24)).decode('utf-8')

@app.before_request
def before_request():
    session_id = request.cookies.get('session_id')
    if not session_id:
        session_id = generate_session_id()
        session['session_id'] = session_id
    
    session_record = session_collection.find_one({'session_id': session_id})
    if session_record:
        # Load session data
        session_data = session_record.get('data', {'session_id'})
        for key, value in session_data.items():
            session[key] = value
    else:
        # Create a new session
        expiration_time = datetime.utcnow() + timedelta(minutes=15)  # Set session lifetime
        session_collection.insert_one({
        'session_id': session_id,
        'data': {},
        'created_at': datetime.utcnow(),
        'expires_at': expiration_time  # Add this line
    })

    request.set_cookie('session_id', session_id, expires=expiration_time)  # Store session_id in g for later access

@app.after_request
def after_request():
    session_id = getattr(g, 'session_id', None)
    if session_id:
        session_data = session.get('access_token')
        if session_data:
            expiration_time = datetime.utcnow() + timedelta(minutes=15)  # Reset session lifetime
            session_collection.update_one(
            {'session_id': session_id},
            {'$set': {'data': session_data, 'updated_at': datetime.utcnow(), 'expires_at': expiration_time}},
        upsert=True
        )
    # Set session cookie to FE

@app.route('/api-autho/validate_session')
def check_access_token(session_id):
    if not session_id:
        return False
    # Query the MongoDB to find the session document with the given session_id
    session_document = session_collection.find_one(
        {
            'session_id': session_id,
            'expires_at': {'$gt': datetime.utcnow()}  # Check that the session hasn't expired
        }
    )
    # If the document is found and has an access_token field, return True
    if session_document and 'access_token' in session_document.get('data', {}):
        return True
    else:
        # If the document or access_token doesn't exist, or the session has expired, return False
        return False

@app.route("/api-autho/authorize", methods=["POST"])
def authorize():
    # Retrieve access token from request
    token = request.headers.get("Authorization")
    if token == None:
        return jsonify({"error": "Missing authorization token"}), 401
    
    try:
        # Decode access token
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=["ES256"])

    except jwt.exceptions.InvalidTokenError as error:
        return jsonify({"error": f"Invalid access token: {error}"}), 401  
    except jwt.exceptions.InvalidSignatureError as error:
        return jsonify({"error": f"Invalid access token: {error}"}), 401 
    except jwt.exceptions.ExpiredSignatureError as error:
        return jsonify({"error": f"Invalid access token: {error}"}), 401
    except jwt.exceptions.InvalidIssuerError as error:
        return jsonify({"error": f"Invalid access token: {error}"}), 401
    except jwt.PyJWTError as error:
        return jsonify({"error": f"{error}"}), 401
    
    # Extract user ID    
    user_id = payload['id']
    scopes=['read','post','delete', user_id]

    #up post do thang user -> post phai cho quyen [read, user_id_1]

    # Check if requested scope is included in user scope

    try:
        payload['scope']
        return jsonify({"error": "Insufficient access rights"}), 401
    except:
        pass

    # Find user in database, if not found, add user
    if find_user(user_id) == False:
        add_user(user_id, scopes)

    # Get user role and scope from database
    try:
        user_scopes = get_user_role_scope(user_id)
    except Exception as error:
        return jsonify({"error": f"Error retrieving user information: {error}"}), 500

    # Check for valid role and scope
    if  user_scopes is None:
        return jsonify({"error": "User not found or invalid"}), 403

    
    # Generate new access token with updated scope if necessary
    new_access_token = None
    new_token_payload = {
            "sub": user_id,
            "scopes": scopes,
            "exp": datetime.utcnow() + timedelta(minutes=15),
        }
    new_access_token = jwt.encode(new_token_payload, SECRET_KEY, algorithm="ES256")

    # Save to Session Server side
    if new_access_token:
        access_token = new_access_token
        set_token(access_token)
        session_id = request.cookies.get('session_id')

    return jsonify({"message": "Access token set in session", "session_id":session_id}),200

def set_token(access_token):
    session['access_token'] = access_token
    return 


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5013)
