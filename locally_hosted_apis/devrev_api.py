from flask import Flask, render_template, request, jsonify
import json
import sys
import os
from datetime import datetime
import requests


from rag_agent import token
from rag_agent import serverHandler

TAVILY_API_KEY = "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"
access_token = "ya29.a0AZYkNZhRCtH1m2Rhuo32QzLvKquNvgBtBj68a8T7L9rf-4CXOdNAAm8_ljcuaPvrHdW6lUg5pvz5pOsKwcdihuvScIsYmGDhbTjcAn5-lTac58tDTet73PVwDL2hZOcTWYTM-BAoLaze5nY5F3fKupdGd4Fb0VXtsumwLM-lPwaCgYKAUgSARMSFQHGX2MiSv-sR4oCvgtz0ZfmdKsIKg0177"

app = Flask(__name__)

server = serverHandler(vdb_path="updated_vectordb",TAVILY_API_KEY=TAVILY_API_KEY)

@app.route('/rag_message', methods=['POST'])
def rag_message():

    try:
        data = request.get_json()
        token1 = token(data["username"],data["message"],data["course"])
        final_token = server.handle_token_rag(token1)


        generated_response = final_token.response
        data["response"] = generated_response
        return jsonify({"status": "success", "message": "Message saved", "response": generated_response}), 200
                
    except Exception as e:
        return jsonify({"error": "Error Generating Response","message":str(e)}), 500

@app.route('/web_message', methods=['POST'])
def web_message():

    try:
        data = request.get_json()
        token1 = token(data["username"],data["message"],data["course"])
        final_token = server.handle_token_web(token1)


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
    app.run(host='0.0.0.0', port=5000, debug=True)