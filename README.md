# 📘 README: AI Assistant Skills for Online Course Platform

This assistant is designed to support students across various academic topics such as **Biology**, **Linguistics**, **Computer Science**, **Python Programming**, **Calculus**, and **Software Engineering**. It offers help in answering academic queries, providing logistics information for courses, and managing study schedules.

# Drive Link for Demo and ppt
https://drive.google.com/drive/folders/1w0c6QvOwNwAMBjCuIPPgDr5HPm1H3oLh?usp=drive_link
---

## 🔧 Skills Overview

### 1. `Get_questions`

**Purpose:**  
Retrieve frequently asked questions from previous student logs for a specific course. This feature is locally hosted.

**Usage:**  
- Used only when the query is about **logistics** (e.g., deadlines, grading, syllabus).
- Requires a `Course_name` field present in the user's request.
- Only the **main topic** from each FAQ is returned.

**Important Rules:**
- Do **not** use any other skill when using this.
- If `Course_name` is **missing**, reply:  
  > "The course name is not present in the article."  
  And provide the **list of available courses** directly.

---

### 2. `AddGoogleCalendarEvent`

We have created Operations feature called Add_gevent
**Purpose:**  
Add academic events (like assignment deadlines, exam reminders, etc.) to a student’s calendar.

**Usage:**  
- Automatically assumes the **Asia/Kolkata** timezone.
- Triggered when students ask to **add an event** (e.g., “remind me of the quiz tomorrow”).

---

### 3. `RAG`

**Purpose:**  
Answer academic questions by retrieving information from course materials using **Retrieval-Augmented Generation**. The data is vectorized and saved in local storage. This feature is locally hosted.

**Usage:**  
- First choice when the student asks a question on course content.
- Summarized responses must include:
  - **Lecture number**
  - **Week number**

---

### 4. `WebScrape`

**Purpose:**  
Provide external context if `RAG` is **not sufficient** or **not relevant**.

**Usage:**  
- Used only **if RAG fails** to provide an adequate or relevant answer.
- When summarizing, always include **relevant source links**.

---

## ✅ Assistant Behavior Summary

- **Primary Focus:** Academic support in biology, linguistics, CS, Python, calculus, software engineering.
- **Polite Redirection:** Gently guide students back to academic topics if the query goes off-track.
- **Course Logistics:** Use `Get_questions` with `Course_name`, and do not mix it with other skills.
- **Calendar Support:** Use `AddGoogleCalendarEvent` for event reminders (default to Asia/Kolkata).
- **Contextual Help:** Use `RAG` for academic queries and fall back to `WebScrape` if needed.
