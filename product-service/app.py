#!/usr/bin/env python3
import json
import requests
from flask import jsonify, request, Flask
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()  

mongodb_api = os.getenv('API_KEY')
db_endpoint = os.getenv('DB_ENDPOINT')
AUTHO_SERVER_URL = os.getenv('AUTHO_SERVER')
header = {
    'Content-Type': 'application/json',
    'Access-Control-Request-Headers': '*',
    'api-key': mongodb_api
}

#Admin: insert, update, delete
#User: find info

def isDuplicate(id: str):
    action = db_endpoint + "findOne"
    payload = json.dumps({
        "collection": "Products",
        "database": "ATM",
        "dataSource": "ROSY",
        "filter": {"id": id}
    })
    r = requests.post(action, headers=header, data=payload)
    result = json.loads(r.text)['document']
    return result is not None

@app.route('/api-product/insert-product', methods=['POST'])
def insert_product():
    session_id = request.cookies.get('session_id')
    #app.logger.warning(session_id)
    # Check if the session_id cookie was found
    if session_id is None:
        return jsonify({"info": "Session ID not found in cookies"}), 404
    else:
        # If the session_id cookie is not found, handle the absence accordingly
        pass
    #app.logger.warning(auth_service_url)
    try:
        response = requests.post(AUTHO_SERVER_URL+"get-scope",cookies={'session_id': session_id}).json()
        #app.logger.info(response)
        access_token =  response['access_token']
        #app.logger.info(f"Log:{access_token}")

    except Exception as e:
        return jsonify({"info": "Access token not found in cookies"}), 404
    if ("post" and "admin" in access_token['scopes']):
        try:
            json_req = request.get_json()
            app.logger.info(f"Log:{json_req}")

        except Exception as ex:
            return jsonify(info='Request Body incorrect json format: ' + str(ex)),442

        # Trim input body
        json_body = {}
        for key, value in json_req.items():
            if isinstance(value, str):
                json_body.setdefault(key, value.strip())
            else:
                json_body.setdefault(key, value)

        _id = json_body.get('product_id')
        title = json_body.get('title')
        price = json_body.get('price')
        if isDuplicate(_id):
            return jsonify(info="Product Already Existed"),442
        else:
            action = db_endpoint + "insertOne"
            payload = json.dumps({
                "collection": "Products",
                "database": "ATM",
                "dataSource": "ROSY",
                "document": {
                    'id': _id,
                    'title': title,
                    'price': price
                }
            })
            r = requests.post(action, headers=header, data=payload)
            return jsonify(info="Insert Product Success"),200
    else:
         return jsonify(info=f"You dont have permission to insert"),403


@app.route('/api-product/delete-product', methods=['POST'])
def delete_product():
    session_id = request.cookies.get('session_id')
    #app.logger.warning(session_id)
    # Check if the session_id cookie was found
    if session_id is None:
        return jsonify({"info": "Session ID not found in cookies"}), 404
    else:
        # If the session_id cookie is not found, handle the absence accordingly
        pass
    #app.logger.warning(auth_service_url)
    try:
        response = requests.post(AUTHO_SERVER_URL+"get-scope",cookies={'session_id': session_id}).json()
        #app.logger.info(response)
        access_token =  response['access_token']
        #app.logger.info(f"Log:{access_token}")

    except Exception as e:
        return jsonify({"info": "Access token not found in cookies"}), 404
    
    if ("delete" and "admin" in access_token['scopes']):
        try:
            request_data = request.get_json()
            app.logger.info(f"Log:{request_data}")
        except Exception as ex:
            return jsonify(info='Request Body incorrect json format: ' + str(ex)),442
        
        _id = request_data.get('product_id')
        app.logger.info(f"LogID = :{_id}")
        if _id is None:
            return jsonify(info="Missing 'id' in the request data"),400
        
        action = db_endpoint + "deleteOne"
        payload = json.dumps({
            "collection": "Products",
            "database": "ATM",
            "dataSource": "ROSY",
            "filter": {"id": _id}
        })

        r = requests.post(action, headers=header, data=payload)
        result = json.loads(r.text)

        if result.get('deletedCount', 0) > 0:
            return jsonify(info="Product deleted successfully"),200
        else:
            return jsonify(info="Product not found or could not be deleted"),404  
    else:
         return jsonify(info=f"You dont have permission to delete"),403
    
@app.route('/api-product/update-product', methods=['POST'])
def update_product():
    session_id = request.cookies.get('session_id')
    #app.logger.warning(session_id)
    # Check if the session_id cookie was found
    if session_id is None:
        return jsonify({"info": "Session ID not found in cookies"}), 404
    else:
        # If the session_id cookie is not found, handle the absence accordingly
        pass
    #app.logger.warning(auth_service_url)
    try:
        response = requests.post(AUTHO_SERVER_URL+"get-scope",cookies={'session_id': session_id}).json()
        #app.logger.info(response)
        access_token =  response['access_token']
        #app.logger.info(f"Log:{access_token}")

    except Exception as e:
        return jsonify({"info": "Access token not found in cookies"}), 404
    if ("post" and "admin" in access_token['scopes']):
        try:
            json_req = request.get_json()
            app.logger.info(f"Log = :{json_req}")

        except Exception as ex:
            return jsonify(info='Request Body incorrect json format: ' + str(ex)),442

        # Trim input body
        json_body = {}
        for key, value in json_req.items():
            if isinstance(value, str):
                json_body.setdefault(key, value.strip())
            else:
                json_body.setdefault(key, value)

        _id = json_body.get('product_id')
        title = json_body.get('title')
        price = json_body.get('price')


        if _id is None:
            return jsonify(info="Missing 'id' in the request data"),400

        action_find = db_endpoint + "findOne"
        filter_find = {"id": _id}
        payload_find = json.dumps({
            "collection": "Products",
            "database": "ATM",
            "dataSource": "ROSY",
            "filter": filter_find
        })
        r_find = requests.post(action_find, headers=header, data=payload_find)
        result_find = json.loads(r_find.text)['document']

        if result_find is None:
            return jsonify(info="Product not found"),404
        else:
            update_fields = {}
            if title:
                update_fields['title'] = title
            if price:
                update_fields['price'] = price

            action_update = db_endpoint + "updateOne"
            payload_update = json.dumps({
                "collection": "Products",
                "database": "ATM",
                "dataSource": "ROSY",
                "filter": filter_find,
                "update": {"$set": update_fields}
            })
            r_update = requests.post(action_update, headers=header, data=payload_update)
            result_update = json.loads(r_update.text)

            if result_update.get('modifiedCount', 0) > 0:
                return jsonify(info="Product updated successfully"),200
            else:
                return jsonify(info="Product could not be updated"),500
    else:
         return jsonify(info=f"You dont have permission to update"),403

@app.route('/api-product/read-product', methods=['POST'])
def get_product_by_title():
    session_id = request.cookies.get('session_id')
    #app.logger.warning(session_id)
    # Check if the session_id cookie was found
    if session_id is None:
        return jsonify({"info": "Session ID not found in cookies"}), 404
    else:
        # If the session_id cookie is not found, handle the absence accordingly
        pass
    #app.logger.warning(auth_service_url)
    try:
        response = requests.post(AUTHO_SERVER_URL+"get-scope",cookies={'session_id': session_id}).json()
        #app.logger.info(response)
        access_token =  response['access_token']
        #app.logger.info(f"Log:{access_token}")

    except Exception as e:
        return jsonify({"info": "Access token not found in cookies"}), 404
    if ("read" in access_token['scopes']):
        try:
            request_data = request.get_json()
        except  Exception as ex:
            return jsonify(info='Request Body incorrect json format: ' + str(ex)),442
        title = request_data.get('title')
        if title is None:
            return jsonify(info="Missing 'title' parameter in the request"), 400

        action_find = db_endpoint + "findOne"
        filter_find = {"title": title}
        payload_find = json.dumps({
            "collection": "Products",
            "database": "ATM",
            "dataSource": "ROSY",
            "filter": filter_find
        })
        r_find = requests.post(action_find, headers=header, data=payload_find)
        response_data = json.loads(r_find.text)
        
        if isinstance(response_data, str):
            # Handle the case where the response is a string (error message, not a document)
            return jsonify(data=response_data), 404

        result = response_data.get('document')

        if not result:
            return jsonify(data="Product not found"), 404

        # If 'document' is a single dictionary
        product_info = {
            'id': result.get('id'),
            'title': result.get('title'),
            'price': result.get('price')
        }
        return jsonify(info=product_info), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8888,debug=True)