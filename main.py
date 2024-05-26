import requests
import json
import os
import uuid
from dotenv import load_dotenv
from flask import Flask, request, jsonify, make_response
import threading

app = Flask(__name__)
load_dotenv()

commands = {}

# command schema
class Command:
    def __init__(self, id, status, data):
        self.id = id
        self.status = status
        self.data = data

def generate_content_thread(command_id, data):
    try:
        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={os.getenv("GEMINI_KEY")}'
        headers = {
            'Content-Type': 'application/json'
        }
        
        commands[command_id].status = 'generating'
        
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            commands[command_id].status = 'done'
            commands[command_id].result = response.json()
        else:
            commands[command_id].status = 'error'
            commands[command_id].result = response.text
    except Exception as e:
        commands[command_id].status = 'failed'
        commands[command_id].result = str(e)

@app.route('/', methods=['POST'])
def generate_content():
    prompt = request.form.get('prompt')
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    
    data = {
        'contents': [
            {
                'parts': [
                    {
                        'text': prompt
                    }
                ]
            }
        ]
    }
    
    command_id = str(uuid.uuid4())
    command = Command(command_id, 'started', data)
    commands[command_id] = command
    
    task_thread = threading.Thread(target=generate_content_thread, args=(command_id, data))
    task_thread.start()
    
    response_data = {"command_id": command_id, "status_url": f"/status/{command_id}"}
    
    return jsonify(response_data), 202

@app.route('/status/<string:command_id>', methods=['GET'])
def get_status(command_id):
    if command_id in commands:
        command = commands[command_id]
        if command.status == 'done' or command.status == 'error' or command.status == 'failed':
            return jsonify({'status': command.status, 'result': command.result})
        else:
            return jsonify({'status': command.status})
    else:
        return jsonify({'error': 'Invalid command ID'}), 404

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5555)
