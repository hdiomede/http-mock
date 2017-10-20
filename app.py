import os
import redis
import json
from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from redis import ConnectionError


app = Flask(__name__)
auth = HTTPBasicAuth()

r = redis.from_url("redis://127.0.0.1:6379/1")

try:
    r.ping()
except ConnectionError:
    exit(0)

users = {
    "john": "hello",
    "susan": "bye"
}


@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None



@app.route('/')
def index():
    return 'Hello World!'



@app.route('/<api>', methods=['POST'])
def create_record(api):
    id = r.incr(api, amount=1)
    payload = request.json
    payload['id'] = id
    r.set(api + ":" + str(id), json.dumps(payload))
    content = r.get(api + ":" + str(id))
    resp = jsonify(json.loads(content))
    return resp



@app.route('/<api>/<id>', methods=['GET'])
def get_record(api, id):
    content = r.get(api + ":" + str(id))
    resp = jsonify(json.loads(content))
    return resp



@app.route('/<api>/<id>', methods=['PUT'])
def create_record(api, id):
    content = r.get(api + ":" + str(id))
    payload = request.json
    r.set(api + ":" + str(id), json.dumps(payload))
    content = r.get(api + ":" + str(id))
    resp = jsonify(json.loads(content))
    return resp



@app.route('/<api>/<id>', methods=['DELETE'])
def delete_record(api, id):
    return ''



@app.route('/<api>', methods=['GET'])
def get_records(api):
    result = { api : []}

    for key in r.scan_iter(api + ":*"):
        result[api].append(json.loads(r.get(key)))

    resp = jsonify(result)
    resp.status_code = 200
    return resp


    
@app.route('/clean', methods=['DELETE'])
@auth.login_required
def clean():
    r.flushall()
    return 'DELETED'



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)



