import requests
import json
import time

# Load API keys
with open('config.json') as f:
    config = json.load(f)

TWITTER_BEARER = config['twitter']['bearer_token']
DEVREV_AGENT_TOKEN = config['devrev']['agent_token']

# Headers for Twitter API
TWITTER_HEADERS = {
    "Authorization": f"Bearer {TWITTER_BEARER}",
    "Content-Type": "application/json"
}

# Headers for DevRev Agent API
DEVREV_HEADERS = {
    "Authorization": f"Bearer {DEVREV_AGENT_TOKEN}",
    "Content-Type": "application/json"
}

# Sample tags to track
TRACK_TAGS = ["#myntra", "#support", "#query", "#delivery"]

def fetch_tweets(tag):
    """Fetch recent tweets containing a specific tag."""
    url = f"https://api.twitter.com/2/tweets/search/recent?query={tag}&max_results=10&tweet.fields=text,author_id"
    response = requests.get(url, headers=TWITTER_HEADERS)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []

def send_to_devrev_agent(message, user_id):
    """Send message to DevRev AI agent to generate response."""
    payload = {
        "user_id": user_id,
        "query": message
    }
    devrev_endpoint = "https://api.devrev.ai/v1/agent/respond"
    response = requests.post(devrev_endpoint, headers=DEVREV_HEADERS, json=payload)
    if response.status_code == 200:
        return response.json().get("reply", "")
    return "We’ll get back to you shortly!"

def auto_reply():
    """Main loop to fetch queries and trigger DevRev agent."""
    for tag in TRACK_TAGS:
        posts = fetch_tweets(tag)
        for post in posts:
            tweet_id = post["id"]
            author_id = post["author_id"]
            text = post["text"]

            # Generate AI response
            reply = send_to_devrev_agent(text, author_id)

            # Log to simulate a reply (real reply API can be added)
            print(f"[{author_id}] - {text}")
            print(f"Auto-Reply: {reply}")
            print("-------------------------------------------------")

# Optional: Hook to Discord or Slack using Webhook (extend here)

if __name__ == "__main__":
    while True:
        auto_reply()
        time.sleep(60)  # Run every 1 minute
