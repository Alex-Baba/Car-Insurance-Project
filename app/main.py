from flask import Flask, jsonify, request

app = Flask(__name__)

stores=[
    {'name': 'My Store',
     'items': [ 
         {
            "id":1,
            "vin":"WVWZZZ1JZXW000001",
            "make":"VW",
            "model":"Golf",
            "yearOfManufacture":2018,
            "owner":{
                "id":7,
                "name":"Alice",
                "email":"alice@example.com"
            }
         }
     ]}
]

@app.route('/stores') #http://127.0.0.1:5000/stores
def get_stores():
    return jsonify({'stores': stores})

@app.post('/stores') #http://127.0.0.1:5000/stores
def create_store():
    request_data = request.get_json()
    new_store={
        'name': request_data['name'],
        'items': []
    }
    stores.append(new_store)
    return jsonify(new_store), 201


@app.post('/stores/<string:name>/item') #http://127.0.0.1:5000/stores/<name>/item
def create_item(name):
    request_data = request.get_json()
    for store in stores:
        if store['name'] == name:
            new_item={
                "id": request_data['id'],
                "vin": request_data['vin'],
                "make": request_data['make'],
                "model": request_data['model'],
                "yearOfManufacture": request_data['yearOfManufacture'],
                "owner": {
                    "id": request_data['owner']['id'],
                    "name": request_data['owner']['name'],
                    "email": request_data['owner']['email']
                }
            }
            store['items'].append(new_item)
            return jsonify(new_item), 201
    return jsonify({'message': 'store not found'}), 404

@app.get("/stores/<string:name>") #http://127.0.0.1:5000/stores/<name>
def get_store(name):
    for store in stores:
        if store['name'] == name:
            return jsonify(store)
    return jsonify({'message': 'store not found'}), 404

@app.get("/stores/<string:name>/item") #http://127.0.0.1:5000/stores/<name>/item
def get_items(name):
    for store in stores:
        if store['name'] == name:
            return jsonify(store['items'])
    return jsonify({'message': 'store not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)