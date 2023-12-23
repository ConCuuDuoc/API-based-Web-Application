from flask import Flask, request, jsonify
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from db import get_user_role_scope, find_user, add_user
import json

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)  # take environment variables from .env.

SECRET_KEY_TOKEN = str(os.getenv("SECRET_KEY_TOKEN"))

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True


@app.route("/authorize", methods=["POST"])
def authorize():
    # Retrieve access token from request
    token = request.headers.get("Authorization")
    if token == None:
        return jsonify({"error": "Missing authorization token"}), 401

    try:
        # Decode access token
        payload = jwt.decode(token, SECRET_KEY_TOKEN, algorithms=["HS256"])
        print(payload)
        print(type(payload))
    except jwt.exceptions.InvalidTokenError as error:
        return jsonify({"error": f"Invalid access token: {error}"}), 401    
    
    # Extract user ID    
    user_id = payload['id']
    role = 'user'
    scopes=['read']
    print(user_id)
    # Find user in database, if not found, add user
    if find_user(user_id) == False:
        add_user(user_id, role, scopes)
       
    # Get user role and scope from database
    try:
        user_role, user_scopes = get_user_role_scope(user_id)
    except Exception as error:
        return jsonify({"error": f"Error retrieving user information: {error}"}), 500

    # Check for valid role and scope
    if user_role is None or user_scopes is None:
        return jsonify({"error": "User not found or invalid"}), 403

    # Check if requested scope is included in user scope
    # requested_scope = request.json.get("scopes")
    # if requested_scope is None or requested_scope not in user_scopes:
    #     return jsonify({"error": "Insufficient access rights"}), 403

    # Generate new access token with updated scope if necessary
    new_access_token = None
    new_token_payload = {
            "sub": user_id,
            "scopes": scopes,
            "exp": datetime.utcnow() + timedelta(minutes=15),
        }
    new_access_token = jwt.encode(new_token_payload, SECRET_KEY_TOKEN, algorithm="HS256")

    # Return response
    response = {
        "role": user_role,
        "scopes": user_scopes,
    }
    if new_access_token:
        response["access_token"] = new_access_token.decode()
    print(response)
    return jsonify(response),200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5013,debug=True)



