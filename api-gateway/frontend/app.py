from flask import (Flask, 
                   jsonify, 
                   request, 
                   render_template, 
                   redirect, 
                   url_for, 
                   send_from_directory, 
                   make_response,
                   abort,
                   session)
from dotenv import load_dotenv
import os
import requests
from json import dumps, loads, dump
from requestAPI import validate_user,submit_user,is_logged_in

load_dotenv()
app = Flask(__name__)
app.secret_key = str(os.getenv('SECRET_KEY'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Retrieve cookies from the incoming request
    

    # Handle the POST request when the login form is submitted
    if request.method == 'POST':
        try:
            cookies = request.cookies
            token_encoded = cookies.get('session_id')
            if is_logged_in(token_encoded):
                return render_template('login.html', announce='User already logged in')
        except:
            pass
        # Extract email and password from the form data
        email, password = request.form["email"], request.form["password"]
        check_response = validate_user(email, password)
        app.logger.info(check_response)
        # If the validation fails, return with an error message
        try:
            if "Error" in check_response['info']:
                error_msg = "Invalid password or email"
                return render_template('login.html', error=error_msg)
            # If the validation is successful, render the login page with a success message
            if "Invalid" in check_response['info']:
                error_msg = check_response['info']
                return render_template('login.html', error=error_msg)
            token = check_response['session_id']
            # response = make_response(render_template('login.html', announce='User sign in successfully'))
            
            response = make_response(redirect(url_for('get_dashboard')))

            response.set_cookie('session_id',value=token,max_age=900)
            #email=email,session_id=token
            
            return response
        except Exception as e:
            app.logger.Error(f"An Exception occurred {e}")
            redirect(url_for('login'))

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
        return render_template('register.html', announce=status)

    # Render the register page for GET requests
    return render_template('register.html')


@app.route('/dashboard',methods=["GET"])
def get_dashboard():
    try:
        is_logged = is_logged_in(request.cookies.get('session_id'))
        app.logger.info(f'ISLOGGED: {is_logged}')
        if is_logged:
            return render_template("dashboard.html")
        else:
            raise Exception
    except Exception as e:
        app.logger.error(f"Other Error:{e}")
        return redirect(url_for('login'))

# Route for the root URL ("/")
@app.route('/', methods=['GET'])
#@is_logged_in
def main_page():
    return render_template('index.html', title="NetSec")

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)