import google.generativeai as genai
import re
import json

# LLM Agent class
class LLM_Agent:
    def __init__(self, GEMINI_API_KEY):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def generate_response(self, tok1):
        prompt = (
            f"\n\nHere is an issue object in JSON format:\n{tok1}\n\n"
            "Generate a product documentation section in Markdown format based on the provided issue. "
            "Use details like the issue key, summary, type, status, reporter, and especially the description field to construct a helpful, readable documentation.\n\n"
            "The documentation should include the following sections:\n"
            "1. **Title** - A short title based on the issue key and summary\n"
            "2. **Overview** - A short paragraph summarizing the issue context\n"
            "3. **Details** - A breakdown of issue type, status, reporter, and any useful description\n"
            "4. **Purpose** - Why this issue matters or what it's trying to address\n"
            "5. **Next Steps** - Any implied or explicit next actions or goals if available\n\n"
            "Respond with only the documentation in valid Markdown format. Don't add extra commentary or JSON."
        )

        content = self.model.generate_content(prompt)
        markdown_output = content.candidates[0].content.parts[0].text.strip()

        # 🧹 Remove any markdown code block formatting like ```markdown or ```
        markdown_output = re.sub(r"```(?:markdown)?", "", markdown_output).strip()

        return markdown_output

class serverHandler:
    def __init__(self, GEMINI_API_KEY):
        self.GEMINI_API_KEY = GEMINI_API_KEY

    def handle_token(self, tok1):
        new_model = LLM_Agent(self.GEMINI_API_KEY)
        content = new_model.generate_response(tok1)
        return content
