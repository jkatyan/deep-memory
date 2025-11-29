from flask import Flask, jsonify, request
import json
import sys
import redis
import uuid
app = Flask(__name__)


r = redis.Redis(host='localhost', port=6379, db=0)


@app.route("/api/python", methods=["GET", "POST"])
def hello_world():
    test = {"text": "hello from python"}
    return json.dumps(test)


@app.route("/api/credentials", methods=["POST"])
def post_credentials():
    decoded = request.data.decode('utf-8')
    id = str(uuid.uuid4())
    json_obj = json.loads(decoded)
    print(id, file=sys.stderr)
    print(json.dumps(json_obj, indent=2), file=sys.stderr)

    r.hmset(id, json_obj)

    res = {"uuid": id}
    return jsonify(
        isError=False,
        message="Success",
        statusCode=200,
        data=res
    ), 200
