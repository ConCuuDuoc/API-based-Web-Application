from flask import (Flask, 
                   jsonify, 
                   request, 
                   render_template, 
                   redirect, 
                   url_for, 
                   send_from_directory, 
                   make_response,
                   abort)
from dotenv import load_dotenv
import os
import requests
from json import dumps, loads, dump
from requestAPI import validate_user,submit_user,is_logged_in


load_dotenv()
app = Flask(__name__)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Retrieve cookies from the incoming request
    cookies = request.cookies
    token_encoded = cookies.get('session_id')

    # Check if the user is already logged in
    if is_logged_in(token_encoded):
        return render_template('login.html', announce='User already logged in')
    
    # Handle the POST request when the login form is submitted
    if request.method == 'POST':
        # Extract email and password from the form data
        email, password = request.form["email"], request.form["password"]
        check_response = validate_user(email, password)

        # If the validation fails, return with an error message
        if not check_response:
            error_msg = "Invalid password or email"
            return render_template('login.html', error=error_msg)
        else:
            # If the validation is successful, render the login page with a success message
            email = check_response['email']
            message = check_response['data']
            token = check_response['session_id'] 
            response = make_response(render_template('login.html', announce='User sign in successfully'))
            response.set_cookie('session_id',value=token,max_age=900)
            return response

    # Render the login page for GET requests
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Handle the POST request when the register form is submitted
    if request.method == 'POST':
        # Extract form data
        email, password, retype_password, email = request.form["email"], request.form["password"], request.form["retype_password"], request.form["email"]

        # Check if the passwords match
        if retype_password != password:
            return render_template('register.html', error="Password does not match")
        
        # Attempt to register the user
        status = submit_user(email, password, email)
        if status != "User sign up successfully, please return to login":
            return render_template('register.html', error=status)
        
        # Render the register page with a success message
        return render_template('register.html', anouce=status)

    # Render the register page for GET requests
    return render_template('register.html')

# Route for the root URL ("/")
@app.route('/', methods=['GET'])
def main_page():
    return render_template('index.html', title="Jelwery")# Route for /products/

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5015,debug=True)