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
BLOG_URL = os.getenv("BLOG_URL")
PROD_URL = os.getenv("PROD_URL")


def submit_user(email,password):
    data = {"email":email,"password":password}
    req = requests.post(AUTHEN_URL+"signup",json=data)
    response = req.json()
    return response

def validate_user(email, password):
    data = {"email":email,"password":password}
    req = requests.post(AUTHEN_URL+"login",json=data)
    response = req.json()
    return response

def blog_up(blog_id,title,content,author):
    session_id = request.cookies.get('session_id')
    if session_id:
        data = {"blog_id":blog_id,"title":title,"content":content,"author":author}
        req = requests.post(BLOG_URL+"upload-blog",json=data,cookies={'session_id': session_id})
        response = req.json()
        return response
    return False

def product_insert(product_id,title,price):
    session_id = request.cookies.get('session_id')
    if session_id:
        data = {"product_id":product_id,"title":title,"price":price}
        req = requests.post(PROD_URL+"insert-product",json=data,cookies={'session_id': session_id})
        response = req.json()
        return response
    return False

def product_delete(product_id):
    session_id = request.cookies.get('session_id')
    if session_id:
        data = {"product_id":product_id}
        req = requests.post(PROD_URL+"delete-product",json=data,cookies={'session_id': session_id})
        response = req.json()
        return response
    return False

def product_update(product_id,title,price):
    session_id = request.cookies.get('session_id')
    if session_id:
        data = {"product_id":product_id,"title":title,"price":price}
        req = requests.post(PROD_URL+"update-product",json=data,cookies={'session_id': session_id})
        response = req.json()
        return response
    return False

def product_read(title):
    session_id = request.cookies.get('session_id')
    if session_id:
        data = {"title":title}
        req = requests.post(PROD_URL+"read-product",json=data,cookies={'session_id': session_id})
        response = req.json()
        return response
    return False

def blog_delete(blog_id):
    session_id = request.cookies.get('session_id')
    if session_id:
        data = {"blog_id":blog_id}
        req = requests.post(BLOG_URL+"delete-blog",json=data,cookies={'session_id': session_id})
        response = req.json()
        return response
    return False

def blog_update(blog_id,title,content,author):
    session_id = request.cookies.get('session_id')
    if session_id:
        data = {"blog_id":blog_id,"title":title,"content":content,"author":author}
        req = requests.post(BLOG_URL+"update-blog",json=data,cookies={'session_id': session_id})
        response = req.json()
        return response
    return False

def blog_read(title):
    session_id = request.cookies.get('session_id')
    if session_id:
        data = {"title":title}
        req = requests.post(BLOG_URL+"read-blog",json=data,cookies={'session_id': session_id})
        response = req.json()
        return response
    return False
    
def is_logged_in(session_id,flag=None):
    if session_id:
        if flag is not None:
            req = requests.post(AUTHEN_URL+"validate-session",cookies={'session_id': session_id,"flag":"get-email"}).json()
            try:
                return req
            except:
                pass
        else:
            req = requests.post(AUTHEN_URL+"validate-session",cookies={'session_id': session_id}).json()
            try:
                return not("not" in req['info'])
            except:
                pass
    return False

def delete_session(session_id):
    if session_id:
        req = requests.post(AUTHEN_URL+"delete-session",cookies={'session_id': session_id}).json()
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