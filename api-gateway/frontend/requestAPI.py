from flask import (Flask, 
                   jsonify, 
                   request, 
                   render_template, 
                   redirect, 
                   url_for, 
                   send_from_directory, 
                   make_response,
                   abort)
import requests
import os
from dotenv import load_dotenv
import functools
import sys

# config URL here
load_dotenv()
AUTHEN_URL = os.getenv("AUTHEN_URL")
AUTHO_URL = os.getenv("AUTHO_URL")

def submit_user(email,password):
    data = {"email":email,"password":password}
    req = requests.post(AUTHEN_URL+"signup",json=data)
    response = req.json()
    status = response['status']
    return status

def validate_user(email, password):
    data = {"email":email,"password":password}
    req = requests.post(AUTHEN_URL+"login",json=data)
    response = req.json()
    return response
    
def is_logged_in(session_id):
    if session_id:
        req = requests.post(AUTHEN_URL+"validate-session",cookies={'session_id': session_id}).json()
        try:
            return not("not" in req['info'])
        except:
            pass
    return False

# def is_logged_in_cookies(session_id=None):
#     if session_id == None:
#         session_id = request.cookies.get('session_id')
#     if session_id:
#         req = requests.post(AUTHEN_URL+"validate-session",cookies={'session_id': session_id})
#         try:
#             message = req['message']
#             return True
#         except:
#             return False
    
#     return False

# def is_logged_in_cookies(f):
#     functools.wraps(f)
#     def authed_only_wrapper(*args, **kwargs):
#         session_id = request.cookies.get('session_id')

#         if session_id:
#             try:
#                 response = requests.post(AUTHEN_URL + "validate-session", cookies=session_id)
#                 data = response.json()
#                 if data.get('message'):
#                     return f(*args, **kwargs),data.get('email')
#             except requests.RequestException as e:
#                 # Handle specific exceptions related to requests
#                 print(e)
#             except ValueError:
#                 # Handle JSON decoding error
#                 pass

#         return redirect(url_for('login'))

#     return authed_only_wrapper
    