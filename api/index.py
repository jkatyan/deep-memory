from flask import Flask, jsonify, request
import json
import sys
import redis
import uuid
import os
from textwrap import dedent
from deep_memory import DeepMemory


#=======================================================================
# Initialize Flask app and Redis client
#=======================================================================
app = Flask(__name__)

# Connect to Redis using Vercel
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
r = redis.from_url(redis_url, decode_responses=True)

# Dictionary of user DeepMemory instances
deep_memory_instances = {}


#=======================================================================
# Get or create DeepMemory instance for a user
#=======================================================================
def get_deep_memory(user_id: str, pinecone_key: str, openai_key: str) -> DeepMemory:
    if user_id not in deep_memory_instances:
        deep_memory_instances[user_id] = DeepMemory(
            pinecone_api_key=pinecone_key,
            openai_api_key=openai_key
        )
    return deep_memory_instances[user_id]


#=======================================================================
# Format conversation memory as a string
#=======================================================================
def format_conversation_memory(messages: list) -> str:
    formatted = []
    for msg in messages:
        role = msg.get('role', 'user')
        content = msg.get('content', '')
        
        if isinstance(content, list):
            text_content = content[0].get('text', '') if content else ''
        else:
            text_content = content
        
        formatted.append(f"{role.upper()}: {text_content}")
    
    return "\n\n".join(formatted)


#=======================================================================
# Chat API endpoint
#=======================================================================
@app.route("/api/python", methods=["GET", "POST"])
def call_chatgpt():
    # Parse request data
    decoded = request.data.decode("utf-8")
    json_obj = json.loads(decoded)
    messages = json_obj.get('messages', [])
    metadata = json_obj.get('metadata', {})
    user_id = str(json_obj.get('id'))
    research_enabled = metadata.get('isResearchEnabled', False)
    memorize_enabled = metadata.get('isMemorizeEnabled', False)
    
    # Get credentials from Redis
    credentials = r.hgetall(user_id)

    # Get DeepMemory instance for user
    dm = get_deep_memory(
        user_id=user_id,
        pinecone_key=credentials["pinecone"],
        openai_key=credentials["openAi"]
    )

    # Extract user query
    user_query = messages[-1]["content"][0]["text"] if messages else ""
    prompt = user_query

    # Construct conversation memory
    conversation_memory = format_conversation_memory(messages[-2:] if len(messages) >= 2 else messages)

    # Perform deep research if enabled
    if research_enabled:
        research_result = dm.research(user_query)
        
        # Format research context
        research_context = dedent(f"""
            === RESEARCH CONTEXT ===
            The following information was retrieved from your long-term memory system:

            {research_result}

            === END RESEARCH CONTEXT ===

            Now, please respond to the user's query using the above context where relevant.

            User Query: {user_query}
        """).strip()

        prompt = research_context

    # Generate chat response using OpenAI
    response_text = dm.openai_provider.generate_text(prompt)

    # Add conversation and response to memory
    conversation_with_response = conversation_memory + f"\n\nASSISTANT: {response_text}"
    dm.add_memory(conversation_with_response)

    # If memorize is enabled, process and store memories
    if memorize_enabled:
        dm.process_memories(context_window="")

    # Return chat response
    return {"text": response_text}


#=======================================================================
# Store user credentials API endpoint
#=======================================================================
@app.route("/api/credentials", methods=["POST"])
def post_credentials():
    decoded = request.data.decode("utf-8")
    id = str(uuid.uuid4())
    json_obj = json.loads(decoded)

    r.hset(id, mapping=json_obj)

    res = {"uuid": id}
    return jsonify(isError=False, message="Success", statusCode=200, data=res), 200


#=======================================================================
# Clear Memory API endpoint
#=======================================================================
@app.route("/api/clear-memory", methods=["POST"])
def clear_memory():
    decoded = request.data.decode("utf-8")
    json_obj = json.loads(decoded)
    user_id = str(json_obj.get('id'))
    
    if user_id in deep_memory_instances:
        dm = deep_memory_instances[user_id]
        dm.clear_memories()
        return jsonify(isError=False, message="Memories cleared", statusCode=200), 200
    
    return jsonify(isError=True, message="No memories found", statusCode=404), 404