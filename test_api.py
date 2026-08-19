"""
Exercises every endpoint of the Task Management API against a live
server and records the real request/response pairs to testing_log.json
and a human-readable testing_log.txt (used to generate the report
screenshots and as the API testing evidence for the submission).
"""
import json
import requests

BASE = "http://127.0.0.1:8000"
transcript = []


def call(method, path, **kwargs):
    url = BASE + path
    resp = requests.request(method, url, **kwargs)
    try:
        body = resp.json()
    except ValueError:
        body = resp.text
    entry = {
        "method": method,
        "url": path,
        "request_body": kwargs.get("json") or kwargs.get("data"),
        "status_code": resp.status_code,
        "response_body": body,
    }
    transcript.append(entry)
    print(f"{method:6s} {path:35s} -> {resp.status_code}")
    return resp


# 1. Health check
call("GET", "/")

# 2. Register a user
call("POST", "/auth/register", json={
    "username": "priya_dev",
    "email": "priya@example.com",
    "password": "SecurePass123"
})

# 2b. Duplicate registration -> should fail validation (400)
call("POST", "/auth/register", json={
    "username": "priya_dev",
    "email": "priya@example.com",
    "password": "SecurePass123"
})

# 2c. Invalid registration -> bad email, should fail (422)
call("POST", "/auth/register", json={
    "username": "ab",
    "email": "not-an-email",
    "password": "123"
})

# 3. Login
resp = call("POST", "/auth/login", data={
    "username": "priya_dev",
    "password": "SecurePass123"
})
token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 3b. Login with wrong password -> 401
call("POST", "/auth/login", data={
    "username": "priya_dev",
    "password": "wrongpassword"
})

# 4. Create tasks (CRUD - Create)
task1 = call("POST", "/tasks", json={
    "title": "Design database schema",
    "description": "Model User and Task tables with a one-to-many relationship",
    "priority": "high",
    "status": "in_progress"
}, headers=headers).json()

task2 = call("POST", "/tasks", json={
    "title": "Write API documentation",
    "description": "Document all REST endpoints for the internship submission",
    "priority": "medium"
}, headers=headers).json()

task3 = call("POST", "/tasks", json={
    "title": "Capture Postman-style test screenshots",
    "priority": "low"
}, headers=headers).json()

# 4b. Create task with invalid data -> 422 (title empty)
call("POST", "/tasks", json={"title": ""}, headers=headers)

# 5. List tasks (CRUD - Read / list)
call("GET", "/tasks", headers=headers)

# 5b. Filter tasks by status
call("GET", "/tasks?status_filter=in_progress", headers=headers)

# 6. Get single task (CRUD - Read / detail)
call("GET", f"/tasks/{task1['id']}", headers=headers)

# 6b. Get a task that doesn't exist -> 404
call("GET", "/tasks/9999", headers=headers)

# 7. Update task (CRUD - Update)
call("PUT", f"/tasks/{task1['id']}", json={
    "status": "completed"
}, headers=headers)

# 8. Delete task (CRUD - Delete)
call("DELETE", f"/tasks/{task3['id']}", headers=headers)

# 8b. Confirm deletion -> 404 on re-fetch
call("GET", f"/tasks/{task3['id']}", headers=headers)

# 9. Unauthorized access -> no token, should be 401
call("GET", "/tasks")

# Save transcript
with open("testing_log.json", "w") as f:
    json.dump(transcript, f, indent=2, default=str)

with open("testing_log.txt", "w") as f:
    for e in transcript:
        f.write(f"{e['method']} {e['url']}\n")
        if e["request_body"]:
            f.write(f"  Request:  {json.dumps(e['request_body'])}\n")
        f.write(f"  Status:   {e['status_code']}\n")
        f.write(f"  Response: {json.dumps(e['response_body'])}\n\n")

print("\nSaved testing_log.json and testing_log.txt")
print(f"Total requests tested: {len(transcript)}")
