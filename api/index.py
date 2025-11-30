from flask import Flask, jsonify, request, Response, stream_with_context
import json
import sys
import redis
import uuid
from openai import OpenAI

app = Flask(__name__)
r = redis.Redis(host="localhost", port=6379, db=0)


@app.route("/api/python", methods=["GET", "POST"])
def call_chatgpt():
    decoded = request.data.decode("utf-8")

    json_obj = json.loads(decoded)
    messages = json_obj.get('messages')
    metadata = json_obj.get('metadata', {})
    
    research_enabled = metadata.get('isResearchEnabled', False)
    memorize_enabled = metadata.get('isMemorizeEnabled', False)

    raw = r.hgetall(str(json_obj.get('id')))
    credentials = {k.decode(): v.decode() for k, v in raw.items()}

    client = OpenAI(api_key=credentials["openAi"], timeout=300.0)
    stream = client.responses.create(
        model="gpt-5",
        input=messages[-1]["content"][0]["text"],
        stream=True,
    )

    text = ""
    for event in stream:
        if event.type == "response.output_text.delta":
            text += event.delta

    return {"text": text}


@app.route("/api/credentials", methods=["POST"])
def post_credentials():
    decoded = request.data.decode("utf-8")
    id = str(uuid.uuid4())
    json_obj = json.loads(decoded)
    print(id, file=sys.stderr)
    print(json.dumps(json_obj, indent=2), file=sys.stderr)

    r.hmset(id, json_obj)

    res = {"uuid": id}
    return jsonify(isError=False, message="Success", statusCode=200, data=res), 200