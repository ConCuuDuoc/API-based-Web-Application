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
load_dotenv()  # take environment variables from .env.

PUBLIC_KEY = str(os.getenv("PUBLIC_KEY"))
SECRET_KEY = str(os.getenv('SECRET_KEY'))
token = "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY1ODY4M2FkZTQ4MjZiZWI3ODMzMzg5MiIsImV4cCI6MTcwMzQyODUyM30.biqF5Cj7jxDnWvSrSNCBRY1RLjTTUSt_5pXqtfNE2p9QdPboGbruy0ABzpbx3BrGQbR51wNQzez7aF5P_nVY1g"
payload = jwt.decode(token, SECRET_KEY, algorithms=["ES256"])
print(payload)