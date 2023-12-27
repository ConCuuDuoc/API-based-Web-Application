from flask import Flask, request, jsonify,  session,g
from db import find_user
from pymongo import MongoClient
from datetime import datetime, timedelta
from dotenv import load_dotenv
from bson.objectid import ObjectId
from pymongo.server_api import ServerApi

import os
import base64
import jwt
import json

load_dotenv('./.env')   # take environment variables from .env.

PUBLIC_KEY = str(os.getenv("PUBLIC_KEY"))
SECRET_KEY = str(os.getenv('SECRET_KEY'))
print(PUBLIC_KEY)