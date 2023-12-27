import json
from flask import Flask, jsonify, request
from dotenv import load_dotenv
import os
import requests

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

#User: upload, update, delete 

def is_duplicate_blog(id: str):
    action = db_endpoint + "findOne"
    payload = json.dumps({
        "collection": "Blog",
        "database": "ATM",
        "dataSource": "ROSY",
        "filter": {"id": id}
    })
    r = requests.post(action, headers=header, data=payload)
    
    try:
        result = json.loads(r.text)['document']
        return result is not None
    except KeyError:
        return False

@app.route('/api-blog/upload-blog', methods=['POST'])
def upload_blog():
    session_id = request.cookies.get('session_id')
    app.logger.warning(session_id)
    # Check if the session_id cookie was found
    if session_id is None:
        return jsonify({"info": "Session ID not found in cookies"}), 404
    else:
        # If the session_id cookie is not found, handle the absence accordingly
        pass

    auth_service_url = AUTHO_SERVER_URL+"get-scope"
    app.logger.warning(auth_service_url)
    # response = requests.post(auth_service_url,cookies={'session_id': session_id})
    try:
        response = requests.post(AUTHO_SERVER_URL+"get-scope",cookies={'session_id': session_id}).json()
        app.logger.info(response)
        access_token =  response['access_token']
        app.logger.info(f"Log:{access_token}")

    except Exception as e:
        return jsonify({"info": "Access token not found in cookies"}), 404
    if ("post" in access_token['scopes']):
        try:
            json_req = request.get_json()
        except Exception as ex:
            return jsonify(info='Request Body incorrect json format: ' + str(ex)),442

        # Get user_id from token (Sub - Subject = user_id)
        user_id = access_token['sub']
        # Trim input body
        json_body = {}
        for key, value in json_req.items():
            if isinstance(value, str):
                json_body.setdefault(key, value.strip())
            else:
                json_body.setdefault(key, value)

        id = json_body.get('id')
        title = json_body.get('title')
        content = json_body.get('content')
        author = json_body.get('author')

        if is_duplicate_blog(id):
            return jsonify(data="Blog Already Existed"),442
        else:
            action = db_endpoint + "insertOne"
            payload = json.dumps({
                "collection": "Blog",
                "database": "ATM",
                "dataSource": "ROSY",
                "document": {
                    'id': id,
                    'user_id':user_id,
                    'title': title,
                    'content': content,
                    'author': author
                }
            })
            r = requests.post(action, headers=header, data=payload)
            result = json.loads(r.text)
            for key, value in result.items():
                if key == 'error':
                    return jsonify(info=f'Error, something went wrong {result}'),442
                if key == 'insertedId':
                    return jsonify(info="Upload Blog Success"),200
                else :
                    return jsonify(info=f"Unknow Error {result}"),442
    else:
         return jsonify(info=f"You dont have permission to upload"),403


@app.route('/api-blog/delete-blog', methods=['DELETE'])
def delete_blog():
    session_id = request.cookies.get('session_id')
    app.logger.warning(session_id)
    # Check if the session_id cookie was found
    if session_id is None:
        return jsonify({"error": "Session ID not found in cookies"}), 404
    else:
        # If the session_id cookie is not found, handle the absence accordingly
        pass

    auth_service_url = AUTHO_SERVER_URL+"get-scope"
    app.logger.warning(auth_service_url)
    # response = requests.post(auth_service_url,cookies={'session_id': session_id})
    response = requests.post(AUTHO_SERVER_URL+"get-scope",cookies={'session_id': session_id}).json()
    access_token =  response['access_token']

    if ("delete" in access_token['scopes']):
        request_data = request.get_json()
        id = request_data.get('id')
        if id is None:
            return jsonify(data="Missing 'id' in the request data"),400
        first_action = db_endpoint+"findOne"
        payload = json.dumps({
            "collection": "Blog",
            "database": "ATM",
            "dataSource": "ROSY",
            "filter": {"id": id}
        })
        r = requests.post(first_action, headers=header, data=payload)
#     # It's important to handle potential errors in the response here
        if r.status_code != 200:
            # Handle error (e.g., log it, raise an exception, etc.)
            return None
        result = json.loads(r.text).get('document', None)
        if result:
            # Get user_id yessir
            res = result.get('user_id', None)
            if not (res == access_token['user_id']):
                return jsonify(info=f"You dont have permission to delete this bro"), 403
        else:
            return jsonify(info=f"You dont have permission to delete this bro"), 403
        
        action = db_endpoint + "deleteOne"
        payload = json.dumps({
            "collection": "Blog",
            "database": "ATM",
            "dataSource": "ROSY",
            "filter": {"id": id}
        })

        r = requests.post(action, headers=header, data=payload)
        result = json.loads(r.text)

        if result.get('deletedCount', 0) > 0:
            return jsonify(info="Blog deleted successfully"),200
        else:
            return jsonify(info="Blog not found or could not be deleted"),404
    else:
         return jsonify(info=f"You dont have permission to delete"),403

@app.route('/api-blog/update-blog', methods=['PUT'])
def update_blog():
    session_id = request.cookies.get('session_id')
    app.logger.warning(session_id)
    # Check if the session_id cookie was found
    if session_id is None:
        return jsonify({"error": "Session ID not found in cookies"}), 404
    else:
        # If the session_id cookie is not found, handle the absence accordingly
        pass

    auth_service_url = AUTHO_SERVER_URL+"get-scope"
    app.logger.warning(auth_service_url)
    # response = requests.post(auth_service_url,cookies={'session_id': session_id})
    response = requests.post(AUTHO_SERVER_URL+"get-scope",cookies={'session_id': session_id}).json()
    access_token =  response['access_token']
    if ("write" in access_token['scopes']):
        try:
            json_req = request.get_json()
        except Exception as ex:
            return jsonify(message='Request Body incorrect json format: ' + str(ex)),442

        # Trim input body
        json_body = {}
        for key, value in json_req.items():
            if isinstance(value, str):
                json_body.setdefault(key, value.strip())
            else:
                json_body.setdefault(key, value)

        id = json_body.get('id')
        title = json_body.get('title')
        content = json_body.get('content')
        author = json_body.get('author')

        if id is None:
            return jsonify(data="Missing 'id' in the request data"),400
        
        
        action_find = db_endpoint + "findOne"
        filter_find = {"id": id}
        payload_find = json.dumps({
            "collection":"Blog",
            "database":"ATM",
            "dataSource":"ROSY",
            "filter": filter_find
        })
        r_find = requests.post(action_find, headers=header, data=payload_find)
        result_find = json.loads(r_find.text)['document']

        if result_find is None:
            return jsonify(data="Blog not found"),404
        else:
            first_action = db_endpoint+"findOne"
            payload = json.dumps({
                "collection": "Blog",
                "database": "ATM",
                "dataSource": "ROSY",
                "filter": {"id": id}
            })
            r = requests.post(first_action, headers=header, data=payload)
    #     # It's important to handle potential errors in the response here
            if r.status_code != 200:
                # Handle error (e.g., log it, raise an exception, etc.)
                return None
            result = json.loads(r.text).get('document', None)
            if result:
                # Get user_id yessir
                res = result.get('user_id', None)
                if not (res == access_token['user_id']):
                    return jsonify(info=f"You dont have permission to update this bro"), 403
            else:
                return jsonify(info=f"You dont have permission to update this bro"), 403
        
            update_fields = {}
            if title:
                update_fields['title'] = title
            if content:
                update_fields['content'] = content
            if author:
                update_fields['author'] = author

            action_update = db_endpoint + "updateOne"
            payload_update = json.dumps({
                "collection": "Blog",
                "database": "ATM",
                "dataSource": "ROSY",
                "filter": filter_find,
                "update": {"$set": update_fields}
            })
            r_update = requests.post(action_update, headers=header, data=payload_update)
            result_update = json.loads(r_update.text)

            if result_update.get('modifiedCount', 0) > 0:
                return jsonify(data="Blog updated successfully"),200
            else:
                return jsonify(data="Blog could not be updated"),500
    else:
         return jsonify(info=f"You dont have permission to update"),403

@app.route('/api-blog/read-blog', methods=['GET'])
def get_blog_by_title():
    session_id = request.cookies.get('session_id')
    app.logger.warning(session_id)
    # Check if the session_id cookie was found
    if session_id is None:
        return jsonify({"error": "Session ID not found in cookies"}), 404
    else:
        # If the session_id cookie is not found, handle the absence accordingly
        pass

    auth_service_url = AUTHO_SERVER_URL+"get-scope"
    app.logger.warning(auth_service_url)
    # response = requests.post(auth_service_url,cookies={'session_id': session_id})
    response = requests.post(AUTHO_SERVER_URL+"get-scope",cookies={'session_id': session_id}).json()
    access_token =  response['access_token']
    if ("read" in access_token['scopes']):
        request_data = request.get_json()
        title = request_data.get('title')
        if title is None:
            return jsonify(data="Missing 'title' parameter in the request"),400

        action_find = db_endpoint + "find"
        filter_find = {"title": title}
        payload_find = json.dumps({
            "collection": "Blog",
            "database": "ATM",
            "dataSource": "ROSY",
            "filter": filter_find
        })
        r_find = requests.post(action_find, headers=header, data=payload_find)
        results_find = json.loads(r_find.text)['documents']

        if not results_find:
            return jsonify(data="Blog not found"),404

        blogs = []
        for result in results_find:
            blog_info = {
                'title': result.get('title'),
                'author': result.get('author')
            }
            blogs.append(blog_info)

        return jsonify(data=blogs),200
    else:
         return jsonify(info=f"You dont have permission to read"),403

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7777,debug=True)
