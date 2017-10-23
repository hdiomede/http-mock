import os
import redis
import json
from flask import Flask, request, jsonify
from redis import ConnectionError


app = Flask(__name__)

r = redis.from_url(os.environ.get("REDIS_URL"))

try:
    r.ping()
except ConnectionError:
    exit(0)


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
    r.delete(api + ":" + str(id))
    return 'DELETED'



@app.route('/<api>', methods=['GET'])
def get_records(api):
    result = { api : []}

    for key in r.scan_iter(api + ":*"):
        result[api].append(json.loads(r.get(key)))

    resp = jsonify(result)
    resp.status_code = 200
    return resp


    
@app.route('/clean', methods=['DELETE'])
def clean():
    r.flushall()
    return 'DELETED'



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)



