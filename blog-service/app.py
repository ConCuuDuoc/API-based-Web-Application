import json
from flask import Flask, jsonify, request
from dotenv import load_dotenv
import os
import requests

app = Flask(__name__)
load_dotenv()

mongodb_api = os.getenv('API_KEY')
db_endpoint = os.getenv('DB_ENDPOINT')
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

@app.route('/api/upload_blog', methods=['POST'])
def upload_blog():
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
                'title': title,
                'content': content,
                'author': author
            }
        })
        r = requests.post(action, headers=header, data=payload)
        result = json.loads(r.text)
        for key, value in result.items():
            if key == 'error':
                return jsonify(deta=f'Error, something went wrong {result}'),442
            if key == 'insertedId':
                return jsonify(data="Upload Blog Success"),200
            else :
                return jsonify(data=f"Unknow Error {result}"),442

@app.route('/api/delete_blog', methods=['DELETE'])
def delete_blog():
    request_data = request.get_json()
    id = request_data.get('id')
    if id is None:
        return jsonify(data="Missing 'id' in the request data"),400
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
        return jsonify(data="Blog deleted successfully"),200
    else:
        return jsonify(data="Blog not found or could not be deleted"),404

@app.route('/api/update_blog', methods=['PUT'])
def update_blog():
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

@app.route('/api/get_blog_by_title', methods=['GET'])
def get_blog_by_title():
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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7777, debug=True)
