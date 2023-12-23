import json, requests
from flask import jsonify, request, Flask
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()  

mongodb_api = os.getenv('API_KEY')
db_endpoint = os.getenv('DB_ENDPOINT')
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

@app.route('/api/insert_product', methods=['POST'])
def insert_product():
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
    price = json_body.get('price')
    if isDuplicate(id):
        return jsonify(data="Product Already Existed"),442
    else:
        action = db_endpoint + "insertOne"
        payload = json.dumps({
            "collection": "Products",
            "database": "ATM",
            "dataSource": "ROSY",
            "document": {
                'id': id,
                'title': title,
                'price': price
            }
        })
        r = requests.post(action, headers=header, data=payload)
        return jsonify(data="Insert Product Success"),200


@app.route('/api/delete_product', methods=['DELETE'])
def delete_product():
    request_data = request.get_json()
    id = request_data.get('id')
    if id is None:
        return jsonify(data="Missing 'id' in the request data"),400
    action = db_endpoint + "deleteOne"
    payload = json.dumps({
        "collection": "Products",
        "database": "ATM",
        "dataSource": "ROSY",
        "filter": {"id": id}
    })

    r = requests.post(action, headers=header, data=payload)
    result = json.loads(r.text)

    if result.get('deletedCount', 0) > 0:
        return jsonify(data="Product deleted successfully"),200
    else:
        return jsonify(data="Product not found or could not be deleted"),404  
    
@app.route('/api/update_product', methods=['PUT'])
def update_product():
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
    price = json_body.get('price')

    if id is None:
        return jsonify(data="Missing 'id' in the request data"),400

    action_find = db_endpoint + "findOne"
    filter_find = {"id": id}
    payload_find = json.dumps({
        "collection": "Products",
        "database": "ATM",
        "dataSource": "ROSY",
        "filter": filter_find
    })
    r_find = requests.post(action_find, headers=header, data=payload_find)
    result_find = json.loads(r_find.text)['document']

    if result_find is None:
        return jsonify(data="Product not found"),404
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
            return jsonify(data="Product updated successfully"),200
        else:
            return jsonify(data="Product could not be updated"),500

@app.route('/api/get_product_by_title', methods=['GET'])
def get_product_by_title():
    request_data = request.get_json()
    title = request_data.get('title')
    if title is None:
        return jsonify(data="Missing 'title' parameter in the request"),400

    action_find = db_endpoint + "find"
    filter_find = {"title": title}
    payload_find = json.dumps({
        "collection": "Products",
        "database": "ATM",
        "dataSource": "ROSY",
        "filter": filter_find
    })
    r_find = requests.post(action_find, headers=header, data=payload_find)
    results_find = json.loads(r_find.text)['documents']

    if not results_find:
        return jsonify(data="Product not found"),404

    products = []
    for result in results_find:
        product_info = {
            'id': result.get('id'),
            'title': result.get('title'),
            'price': result.get('price')
        }
        products.append(product_info)

    return jsonify(data=products),200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8888, debug=True)