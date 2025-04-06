from flask import Flask, request, jsonify
from agent_md import serverHandler
import os
import google.generativeai as genai


app = Flask(__name__)
GEMINI_API_KEY = 'AIzaSyDOYMZD7-0f9LHIywUT0xca6edpSfuO8Ic'

server = serverHandler(GEMINI_API_KEY=GEMINI_API_KEY)

srs_filename = "product_srs.md"              

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        issue = data['issue']

        issue_key = issue.get("key", "Unknown_Issue")

        markdown_content = server.handle_token(issue)

        os.makedirs("docs", exist_ok=True)
        shared_filename = os.path.join("docs", "All_Issues_Documentation.md")

        with open(shared_filename, 'a', encoding='utf-8') as doc:
            doc.write(f"\n\n---\n\n## Issue: {issue_key}\n\n")
            doc.write(markdown_content + "\n")
            

        if os.path.exists(srs_filename):
            with open(srs_filename, 'r', encoding='utf-8') as f:
                existing_srs = f.read()
        else:
            existing_srs = "# Product SRS Document\n"

        genai.configure(api_key=GEMINI_API_KEY)
        model_srs = genai.GenerativeModel('gemini-2.0-flash')

        prompt = f"""
        You are a helpful assistant. Here is the current SRS document:
        \n{existing_srs}\n
        And here is a new closed issue that needs to be integrated:
        \n{markdown_content}\n
        Rewrite and summarize the updated SRS document by integrating the new issue. Keep it professional, concise, and in markdown format. dont include the issues separately make it continuous as one product
        """

        response = model_srs.generate_content(prompt)
        updated_srs = response.text

        with open(srs_filename, 'w', encoding='utf-8') as f:
            f.write(updated_srs)

        
        print(f"✅ Issue '{issue_key}' added to '{shared_filename}'")
        return jsonify({'status': "success", 'issue': issue_key})

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({'status': "error", 'message': str(e)})

if __name__ == "__main__":
    app.run(port=5002)
