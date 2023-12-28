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
from requestAPI import validate_user,submit_user,is_logged_in,delete_session,blog_up,blog_delete,blog_update,blog_read,product_insert,product_delete,product_update,product_read

load_dotenv()
app = Flask(__name__)
app.secret_key = str(os.getenv('SECRET_KEY'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Retrieve cookies from the incoming request
    try:
        cookies = request.cookies
        token_encoded = cookies.get('session_id')
        if is_logged_in(token_encoded):
            return redirect(url_for('get_dashboard'))
    except:
        pass
    

    # Handle the POST request when the login form is submitted
    if request.method == 'POST':
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
    # Retrieve cookies from the incoming request
    try:
        cookies = request.cookies
        token_encoded = cookies.get('session_id')
        if is_logged_in(token_encoded):
            return redirect(url_for('get_dashboard'))
    except:
        pass
    # Handle the POST request when the register form is submitted
    if request.method == 'POST':
        # Extract form data
        email, password, retype_password, email = request.form["email"], request.form["password"], request.form["retype_password"], request.form["email"]

        # Check if the passwords match
        if retype_password != password:
            return render_template('register.html', error="Password does not match")
        
        # Attempt to register the user
        status = submit_user(email, password)
        app.logger.info(status)
        if 'Success' in status['info']:
            return redirect(url_for("login"))
        # Render the register page with a success message
        return render_template('register.html', error=status['info'])

    # Render the register page for GET requests
    return render_template('register.html')


@app.route('/dashboard',methods=["GET"])
def get_dashboard():
    try:
        check_response = is_logged_in(request.cookies.get('session_id'),"get-email")
        app.logger.info(f'ISLOGGED: {check_response}')
        if 'logged' in check_response['info']:
            return render_template('dashboard.html',email=check_response['email'])
        else:
            return render_template('dashboard.html',email="Error")
    except Exception as e:
        app.logger.error(f"Other Error:{e}")
        return redirect(url_for('login'))
    
@app.route('/logout',methods=['GET','POST'])
def logout():
    try:
        is_logged = is_logged_in(request.cookies.get('session_id'))
        app.logger.info(f'ISLOGGED: {is_logged}')
        if is_logged:
            delete_session(request.cookies.get('session_id'))
            response = make_response(redirect(url_for('login')))
            response.set_cookie('session_id', value='', max_age=0)
            return response
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

@app.route('/blog', methods=['GET'])
#@is_logged_in
def blog_page():
    
    try:
        is_logged = is_logged_in(request.cookies.get('session_id'))
        app.logger.info(f'ISLOGGED: {is_logged}')
        if is_logged:
            return render_template('blog.html', title="NetSec")
        else:
            raise Exception
    except Exception as e:
        app.logger.error(f"Other Error:{e}")
        return redirect(url_for('login'))

@app.route('/products', methods=['GET'])
#@is_logged_in
def products_page():
    try:
        is_logged = is_logged_in(request.cookies.get('session_id'))
        app.logger.info(f'ISLOGGED: {is_logged}')
        if is_logged:
            return render_template('products.html', title="NetSec")
        else:
            raise Exception
    except Exception as e:
        app.logger.error(f"Other Error:{e}")
        return redirect(url_for('login'))

@app.route('/insert-product', methods=['POST'])
#@is_logged_in
def post_insert_product():
    try:
        is_logged = is_logged_in(request.cookies.get('session_id'))
        app.logger.info(f'ISLOGGED: {is_logged}')
        if is_logged:
            product_id = request.form.get('id')
            title = request.form.get('title')
            price = request.form.get('price')
            app.logger.warning(f"{product_id},{title},{price}")
            check_response = product_insert(product_id,title,price)

            if 'Success' in check_response['info']:
                return render_template('products.html',announce=check_response['info'])
            else:
                return render_template('products.html',error=check_response['info'])
        else:
            raise Exception
    except Exception as e:
        app.logger.error(f"Other Error:{e}")
        return redirect(url_for('products_page'))

@app.route('/update-product', methods=['POST'])
#@is_logged_in
def post_update_product():
    try:
        is_logged = is_logged_in(request.cookies.get('session_id'))
        app.logger.info(f'ISLOGGED: {is_logged}')
        if is_logged:
            product_id = request.form.get('updateId')
            title = request.form.get('updateTitle')
            price = request.form.get('updatePrice')
            app.logger.warning(f"{product_id},{title},{price}")
            check_response = product_update(product_id,title,price)

            if 'Success' in check_response['info']:
                return render_template('products.html',announce=check_response['info'])
            else:
                return render_template('products.html',error=check_response['info'])
        else:
            raise Exception
    except Exception as e:
        app.logger.error(f"Other Error:{e}")
        return redirect(url_for('products_page'))

@app.route('/read-product', methods=['POST'])
#@is_logged_in
def post_read_product():
    try:
        is_logged = is_logged_in(request.cookies.get('session_id'))
        app.logger.info(f'ISLOGGED: {is_logged}')
        if is_logged:
            title = request.form.get('getByTitle')
            app.logger.warning(f"{title}")
            check_response = product_read(title)

            if 'Success' in check_response['info']:
                return render_template('products.html',announce=check_response['info'])
            else:
                return render_template('products.html',error=check_response['info'])
        else:
            raise Exception
    except Exception as e:
        app.logger.error(f"Other Error:{e}")
        return redirect(url_for('products_page'))
    
@app.route('/delete-product', methods=['POST'])
#@is_logged_in
def post_delete_product():
    try:
        is_logged = is_logged_in(request.cookies.get('session_id'))
        app.logger.info(f'ISLOGGED: {is_logged}')
        if is_logged:
            product_id = request.form.get('deleteId')
            app.logger.warning(f"{product_id}")
            check_response = product_read(product_id)

            if 'Success' in check_response['info']:
                return render_template('products.html',announce=check_response['info'])
            else:
                return render_template('products.html',error=check_response['info'])
        else:
            raise Exception
    except Exception as e:
        app.logger.error(f"Other Error:{e}")
        return redirect(url_for('products_page'))
    
    
@app.route('/upload-blog', methods=['POST'])
#@is_logged_in
def post_upload_blog():
    try:
        is_logged = is_logged_in(request.cookies.get('session_id'))
        app.logger.info(f'ISLOGGED: {is_logged}')
        if is_logged:
            blog_id = request.form.get('id')
            title = request.form.get('title')
            content = request.form.get('content')
            author = request.form.get('author')
            app.logger.warning(f"{blog_id},{title},{content},{author}")
            check_response = blog_up(blog_id,title,content,author)

            if 'Success' in check_response['info']:
                return render_template('blog.html',announce=check_response['info'])
            else:
                return render_template('blog.html',error=check_response['info'])
        else:
            raise Exception
    except Exception as e:
        app.logger.error(f"Other Error:{e}")
        return redirect(url_for('blog_page'))

@app.route('/delete-blog', methods=['POST'])
#@is_logged_in
def del_delete_blog():
    try:
        is_logged = is_logged_in(request.cookies.get('session_id'))
        app.logger.info(f'ISLOGGED: {is_logged}')
        if is_logged:
            blog_id = request.form.get('deleteId')
            app.logger.warning(f"{blog_id}")
            check_response = blog_delete(blog_id)

            if 'Success' in check_response['info']:
                return render_template('blog.html',announce=check_response['info'])
            else:
                return render_template('blog.html',error=check_response['info'])
        else:
            raise Exception
    except Exception as e:
        app.logger.error(f"Other Error:{e}")
        return redirect(url_for('blog_page'))

@app.route('/update-blog', methods=['POST'])
#@is_logged_in
def post_update_blog():
    try:
        is_logged = is_logged_in(request.cookies.get('session_id'))
        app.logger.info(f'ISLOGGED: {is_logged}')
        if is_logged:
            blog_id = request.form.get('updateId')
            title = request.form.get('updateTitle')
            content = request.form.get('updateContent')
            author = request.form.get('updateAuthor')
            app.logger.warning(f"{blog_id},{title},{content},{author}")
            check_response = blog_update(blog_id,title,content,author)

            if 'Success' in check_response['info']:
                return render_template('blog.html',announce=check_response['info'])
            else:
                return render_template('blog.html',error=check_response['info'])
        else:
            raise Exception
    except Exception as e:
        app.logger.error(f"Other Error:{e}")
        return redirect(url_for('blog_page'))

@app.route('/read-blog', methods=['POST'])
#@is_logged_in
def get_read_blog():
    try:
        is_logged = is_logged_in(request.cookies.get('session_id'))
        app.logger.info(f'ISLOGGED: {is_logged}')
        if is_logged:
            title = request.form.get('getByTitle')
            app.logger.warning(f"{title}")
            check_response = blog_read(title)

            if 'Success' in check_response['info']:
                return render_template('blog.html',announce=check_response['info'])
            else:
                return render_template('blog.html',error=check_response['info'])
        else:
            raise Exception
    except Exception as e:
        app.logger.error(f"Other Error:{e}")
        return redirect(url_for('blog_page'))
    

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)