from flask import (Flask, 
                   jsonify, 
                   request, 
                   render_template, 
                   redirect, 
                   url_for, 
                   send_from_directory, 
                   make_response,
                   abort)
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import requests
from json import dumps, loads, dump
from RequestAPI import validate_password,submit_user,is_logged_in


load_dotenv()
app = Flask(__name__)

@app.route('/login',methods=['GET','POST'])
def login():
    cookies = request.cookies
    token_encoded = cookies.get('session_id')
    if is_logged_in(token_encoded):
        return render_template('login.html',anouce = 'User already logged in')
    if request.method=='POST':
        username,password = request.form["username"], request.form["password"]
        check_respone = validate_password(username,password)
        if not check_respone:
            error_msg = "Invalid password or username"
            return render_template('login.html',error = error_msg)
        else:
            token = check_respone['token']
            username = check_respone['username']
            response = make_response(render_template('login.html',anouce = 'User sign in successfully'))
            response.set_cookie('session_token',value=token,max_age=3600)
            return response
    return render_template('login.html')

@app.route('/register',methods=['GET','POST'])
def register():
    global redirect_from_register
    if request.method=='POST':
        username,password,retype_password,email = request.form["username"],request.form["password"],request.form["retype_password"],request.form["email"]
        if retype_password!=password:
            return render_template('register.html',error = "Password does not match")
        status = submit_user(username,password,email)
        if status!="User sign up sucessfully, please return to login":
            return render_template('register.html',error = status)
        return render_template('register.html',anouce = status)
    return render_template('register.html')

# Route for the root URL ("/")
@app.route('/', methods=['GET'])
def main_page():
    return render_template('index.html', title="Jelwery")

# Route for /products/
@app.route('/products/', methods=['GET'])
def product_page():
    api_url = f"http://{os.getenv('PRODUCT_SVC_ADDRESS')}/api/allproduct"
    req = requests.get(api_url)
    products =  req.json()
    
    for product in products:
        print(loads(product['category']))
        print('ok')
        product['category'] = loads(product['category'])
    print(products)
    file_path = f"./static/json/products.json"
    dump(products, open(file_path,'w'))
    return render_template('products.html', title="Products")


    
if __name__ == '__main__':
    app.run(host="0.0.0.0")