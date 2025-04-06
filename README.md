# JIRA Webhook Integration Project

# Demo Video link
https://drive.google.com/file/d/1kSbU_uNK_7jlbNX_iWCr5WLlX__3aTXs/view?usp=sharing

# Project Info
This project integrates with JIRA using webhooks to monitor issue status changes. When a JIRA issue's status is modified, the webhook triggers a Python script that processes the update and outputs the result.

## 📦 Features

- Webhook listener using Flask
- Integration with JIRA via ngrok tunnel
- Automatic response on JIRA issue status change
- Simple and lightweight setup

---

## 🚀 Prerequisites

- Python 3.6 or higher
- [ngrok](https://ngrok.com/) (for exposing localhost)
- JIRA access with permission to configure webhooks

---

## 🛠️ Setup Instructions

1. **Clone the repository**
   ```bash
   git clone http://github.com/devrev/iitm-submission-odyssey/tree/main
   cd your-repo-name
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Running the Project

Follow these steps to start the server and connect it to JIRA:

### Step 1 → Run the Python Script

```bash
python3 issues.py
```

### Step 2 → Start ngrok

Expose your local server (on port 5002) to the internet:

```bash
ngrok http 5002
```

Copy the HTTPS URL provided by ngrok (e.g., `https://abcd1234.ngrok.io`).

### Step 3 → Configure JIRA Webhook

1. Go to your JIRA project settings.
2. Navigate to **System > Webhooks**.
3. Create a new webhook with the following:
   - **URL**: Paste the HTTPS URL from ngrok.
   - **Events**: Select issue-related events (e.g., issue updated, status changed).

### Step 4 → Trigger the Webhook

Modify the status of issues in JIRA to trigger the webhook and observe the output in your terminal.

---

## 📝 Notes

- Ensure `issues.py` is listening on port `5002`, or update the ngrok command accordingly.
- Webhook data can be logged or processed further depending on your project requirements.
- ngrok free accounts rotate URLs on restart—remember to update the JIRA webhook URL each time.

---

## 📂 Project Structure

```
your-project/
│
├── issues.py               # Main Flask app that listens for webhook POSTs
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

---

## 📧 Contact

For issues or contributions, please open an issue or pull request.


