from flask import Flask
from flask import request, jsonify
from flask_cors import CORS
from bson.objectid import ObjectId

import json
from pymongo import MongoClient
import datetime

app = Flask(__name__)
CORS(app)
client = MongoClient()
db = client.hindex

@app.route('/setresult', methods=['POST'])
def set_result():
    data = json.loads(request.get_data().decode("UTF-8"))
    collection = db.responses
    print("Key: ", data['key'])
    collection.update_one({'_id': ObjectId(data['key'])},{ '$set': data['result'] }, upsert=False)
    return jsonify({"success":True})
    
@app.route('/', methods=['POST'])
def hello_world():
    data = json.loads(request.get_data().decode("UTF-8"))
    data['date'] = datetime.datetime.utcnow()
    collection = db.responses
    doc = collection.insert_one(data)
    return jsonify({"key":str(doc.inserted_id)})


if __name__ == '__main__':
    app.run()
