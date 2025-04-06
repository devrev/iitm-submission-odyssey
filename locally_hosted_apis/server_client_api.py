from flask import Flask, render_template, request, jsonify
import json
import sys
import os
from datetime import datetime
import requests
from jsonschema import validate, ValidationError


from server import token
from server import serverHandler

from rag_agent import token_r
from rag_agent import serverHandler_r

API_URL_ADD = "http://192.168.1.107:5001/add_log"  # URL of the API server to add_logs
API_URL_VIEW = "http://192.168.1.107:5001/view_logs"  # URL of the API server to view_logs
app = Flask(__name__)

from dotenv import load_dotenv
load_dotenv()

TAVI_API_KEY = os.getenv('TAVI_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
access_token = "ya29.a0AZYkNZhRCtH1m2Rhuo32QzLvKquNvgBtBj68a8T7L9rf-4CXOdNAAm8_ljcuaPvrHdW6lUg5pvz5pOsKwcdihuvScIsYmGDhbTjcAn5-lTac58tDTet73PVwDL2hZOcTWYTM-BAoLaze5nY5F3fKupdGd4Fb0VXtsumwLM-lPwaCgYKAUgSARMSFQHGX2MiSv-sR4oCvgtz0ZfmdKsIKg0177"
global_answer = {"xyz": "asd"}

server = serverHandler(GEMINI_API_KEY=GEMINI_API_KEY,TAVILY_API_KEY=TAVI_API_KEY,vdb_path="updated_vectordb", faqdb_path="updated_faqdb", assigndb_path="updated_assigndb")
server_dev = serverHandler_r(vdb_path="updated_vectordb",TAVILY_API_KEY=TAVI_API_KEY)

schema = {
    "type": "object",
    "properties": {
        "username": {"type": "string"},
        "timestamp": {"type": "string"},
        "message": {"type": "string"},
        "web_search": {"type": "boolean"},
        "course": {"type": "string"}
    },
    "required": ["username", "timestamp", "message", "web_search", "course"]
}
delete_schema = {
    "type": "object",
    "properties": {
        "username": {"type": "string"}
    },
    "required": ["username"]
}

course_names = {
        'introduction to biology' : 'biology',
        'introduction to linguistics' : 'linguistics',
        'introduction to computer science and programming in python' : 'pyprog',
        'differential calculus' : 'calculus',
        'software engineering' : 'swe'
    }
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')

@app.route('/chatbox.html')
def chatbox():
    return render_template('chatbox.html')

@app.route('/course.html')
def course():
    return render_template('course.html')

@app.route('/assignment.html')
def assignment():
    return render_template('assignment.html')

@app.route('/devlog.html')
def devlog():
    return render_template('devlog.html')

@app.route('/data/courses', methods=['GET'])
def get_courses():
    try:
        username = request.args.get("username", "guest")

        user_file = os.path.join("static/data/users", f"{username}.txt")
        with open(user_file, "r") as file:
            lines = [line.strip() for line in file.readlines() if line.strip()]
        
        courses = []
        for line in lines:
            match = line.strip().split(" - ")
            if len(match) == 2:
                code, name = match
                courses.append({"code": code.split(". ")[1], "name": name})

        return jsonify(courses), 201
    except Exception as e:
        return jsonify({"error": "Error recovering courses"}), 500

@app.route('/get_assignment', methods=['GET'])
def get_assignment():
    try:
        course = request.args.get("course", 'dummy').lower()  # Get course name from URL
        course_name = course_names.get(course, 'dummy')
        file_path = os.path.join("static/data/assignments", f"{course_name}.txt")

        with open(file_path, 'r') as file:
            content = file.read()
            return jsonify({"content": content}), 200
    except Exception as e:
        return jsonify({"error": "Error getting assignment"}), 500

@app.route('/fetch_logs', methods=['GET'])
def fetch_logs():
    """Fetch logs from the external server and return them."""
    try:
        response = requests.get(API_URL_VIEW)
        response.raise_for_status()
        return response.text, 200
    except Exception as e:
        return f"<p>Error fetching logs: {str(e)}</p>", 500

@app.route('/show_message/<session_object>', methods=['GET'])
def show_message(session_object):
    print(session_object)
    if(global_answer[session_object]):
        return jsonify(global_answer[session_object])
    return jsonify({})

@app.route('/save_message', methods=['POST'])
def save_message():

    try:
        data = request.get_json()
        validate(instance=data, schema=schema)

        token1 = token(data["username"],data["timestamp"],data["message"], data["web_search"],data["course"])
        final_token = server.handle_token(token1)


        generated_response = final_token.response
        data["response"] = generated_response
        try:
            response = requests.post(API_URL_ADD, json=data)
            if response.status_code == 201:
                print("Log added successfully to API")
                return jsonify({"status": "success", "message": "Message saved", "response": generated_response}), 200
            else:
                print("Failed to add log:", response.json())
                return jsonify({"status": "success", "message": "Failed to add log", "response": generated_response}), 201

        except Exception as e:
            print("Error communicating with API:", str(e))
            return jsonify({"status": "success", "message": "Error communicating with Logs", "response": generated_response}), 202
        
    except ValidationError as e:
        return jsonify({"error": "Invalid JSON format", "message": str(e)}), 400
    except Exception as e:
        exception_string = str(e)
        print('server exception:',exception_string)
        return jsonify({"error": "Error Generating Response","message":str(e)}), 500


@app.route('/delete_chat_history', methods=['POST'])
def delete_chat_history():
    try:
        data = request.get_json()
        validate(instance=data, schema=delete_schema)
        username = data.get("username", "guest")  # Default to "guest" if no username
        server.delete_user(username)
        return jsonify({"status": "success", "message": "Chat history file deleted"}), 200
    except ValidationError as e:
        return jsonify({"error": "Invalid JSON format", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Error deleting chat history", "message": str(e)}), 500

@app.route('/webhook_message', methods=['POST'])
def webhook_message():
    data= request.get_json()
    message = data["message"]
    session_object = data["session_object"]


    headers = {
        'Authorization': f'Bearer eyJhbGciOiJSUzI1NiIsImlzcyI6Imh0dHBzOi8vYXV0aC10b2tlbi5kZXZyZXYuYWkvIiwia2lkIjoic3RzX2tpZF9yc2EiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOlsiamFudXMiXSwiYXpwIjoiZG9uOmlkZW50aXR5OmR2cnYtdXMtMTpkZXZvLzFFeE1jM2Fma2s6ZGV2dS81MjgiLCJleHAiOjE4Mzg1NDQ2MTAsImh0dHA6Ly9kZXZyZXYuYWkvYXV0aDBfdWlkIjoiZG9uOmlkZW50aXR5OmR2cnYtdXMtMTpkZXZvL3N1cGVyOmF1dGgwX3VzZXIvb2lkY3xwYXNzd29yZGxlc3N8ZW1haWx8NjdmMGY2NzYzMmIxNTcwYzZiNjA3NTcwIiwiaHR0cDovL2RldnJldi5haS9hdXRoMF91c2VyX2lkIjoib2lkY3xwYXNzd29yZGxlc3N8ZW1haWx8NjdmMGY2NzYzMmIxNTcwYzZiNjA3NTcwIiwiaHR0cDovL2RldnJldi5haS9kZXZvX2RvbiI6ImRvbjppZGVudGl0eTpkdnJ2LXVzLTE6ZGV2by8xRXhNYzNhZmtrIiwiaHR0cDovL2RldnJldi5haS9kZXZvaWQiOiJERVYtMUV4TWMzYWZrayIsImh0dHA6Ly9kZXZyZXYuYWkvZGV2dWlkIjoiREVWVS01MjgiLCJodHRwOi8vZGV2cmV2LmFpL2Rpc3BsYXluYW1lIjoiY3MyMWIwMzQiLCJodHRwOi8vZGV2cmV2LmFpL2VtYWlsIjoiY3MyMWIwMzRAc21haWwuaWl0bS5hYy5pbiIsImh0dHA6Ly9kZXZyZXYuYWkvZnVsbG5hbWUiOiJDczIxYjAzNCIsImh0dHA6Ly9kZXZyZXYuYWkvaXNfdmVyaWZpZWQiOnRydWUsImh0dHA6Ly9kZXZyZXYuYWkvdG9rZW50eXBlIjoidXJuOmRldnJldjpwYXJhbXM6b2F1dGg6dG9rZW4tdHlwZTpwYXQiLCJpYXQiOjE3NDM5MzY2MTAsImlzcyI6Imh0dHBzOi8vYXV0aC10b2tlbi5kZXZyZXYuYWkvIiwianRpIjoiZG9uOmlkZW50aXR5OmR2cnYtdXMtMTpkZXZvLzFFeE1jM2Fma2s6dG9rZW4vSEVuVVJRbkQiLCJvcmdfaWQiOiJvcmdfVVRXUHB1eW4xZGkxTE5vQyIsInN1YiI6ImRvbjppZGVudGl0eTpkdnJ2LXVzLTE6ZGV2by8xRXhNYzNhZmtrOmRldnUvNTI4In0.iOMy61eLGqxQbE5kirKv30VURiB-ZvxYhv9RFMWOX8i-1qVzNKfgmSmHOtuLtipbR08JOe3MoF0qSZbCBmfEYXBgk111GKuDBhQP-XxIQbTWMKoEG5Lf6wNVxHF1MAic0GapDhe1I2jjwTpuiIkWgkEdy19FZG-4bEgRInRHMXBZnrtQhGW6JwTa2a2SOYULjzZyGX_CrVBKdrQBdzQraoAJ7ns1GLW3M3PZ5ivNTVdGB0SEt0NMdwag9sNtK5kUMBti9pLuTJh42MTV_zJTOB1A33wnaNs7evd71hhqYFiHAg6ITF6zBEkMwV5TUiTJhjXAdoEWwzNRpusFkMh1EQ',
        'Content-Type': 'application/json'
    }
    temp= {
        "agent": "don:core:dvrv-us-1:devo/1ExMc3afkk:ai_agent/31",
        "context": {
            "initial": ""
        },
        "event": {
            "input_message": {
            "message": message
            }
        },
        "session_object": session_object,
        "webhook_target": {
            "webhook": "don:integration:dvrv-us-1:devo/1ExMc3afkk:webhook/XfFIqdE4"
        },
        "target": "webhook_target"
        }
    url="https://api.devrev.ai/ai-agents.events.execute-async"

    response = requests.post(url, headers=headers, json=temp)
    return {}



@app.route('/webhook', methods=['POST'])
def webhook():
    data =request.get_json()
    if 'message' in data['ai_agent_response']:
        reply = data['ai_agent_response']['message']
        session_object = data['ai_agent_response']["session_object"]
        print("session_object",session_object)
        print("reply",reply)
        global_answer[session_object] = reply
 
    print("webhook data",data)
    return{}
    # return {"challenge": data["verify"]["challenge"]}

@app.route('/rag_message', methods=['POST'])
def rag_message():

    try:
        data = request.get_json()
        token1 = token_r(data["username"],data["message"],data["course"])
        final_token = server_dev.handle_token_rag(token1)


        generated_response = final_token.response
        data["response"] = generated_response
        return jsonify({"status": "success", "message": "Message saved", "response": generated_response}), 200
                
    except Exception as e:
        return jsonify({"error": "Error Generating Response","message":str(e)}), 500

@app.route('/web_message', methods=['POST'])
def web_message():

    try:
        data = request.get_json()
        token1 = token_r(data["username"],data["message"],data["course"])
        final_token = server_dev.handle_token_web(token1)


        generated_response = final_token.response
        data["response"] = generated_response
        return jsonify({"status": "success", "message": "Message saved", "response": generated_response}), 200
                
    except Exception as e:
        return jsonify({"error": "Error Generating Response","message":str(e)}), 500
    

@app.route('/add_event', methods=['POST'])
def add_event():
    print("add_event")
    url = 'https://www.googleapis.com/calendar/v3/calendars/primary/events'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    try:
        data = request.get_json()
        event_data = {
            "summary": data["summary"],
            "start": {
                "dateTime": data["start_time"],
                "timeZone": data["timezone"]
            },
            "end": {
                "dateTime": data["end_time"],
                "timeZone": data["timezone"]
            }
        }
        print("event_data",event_data)
        response = requests.post(url, headers=headers, json=event_data)
        
        return jsonify({"status": "success", "message": "Event added successfully"}), 200
    except Exception:
        return jsonify({"status": "error", "message": "Failed to add event"}), 500
    



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
