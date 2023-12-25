import requests
import os
from dotenv import load_dotenv

# config URL here
load_dotenv()
AUTHEN_URL = os.getenv("AUTHEN_URL")
AUTHO_URL = os.getenv("AUTHO_URL")

def submit_user(email,password):
    data = {"email":email,"password":password}
    req = requests.post(AUTHEN_URL+"signup",json=data)
    respone = req.json()
    status = respone['status']
    return status

def validate_user(email, password):
    data = {"email":email,"password":password}
    req = requests.post(AUTHEN_URL+"login",json=data)
    respone = req.json()
    try:
        message = respone['data']
        mail = respone['email']
        session_id = response['session_id']
        return respone
    except:
        return False
    
def is_logged_in(session_id):
    if session_id:
        cookies = {'session_id':session_id}
        req = requests.post(AUTHEN_URL+"verify-session",cookies=cookies)
        try:
            message = req['message']
            return True
        except:
            return False
    return False