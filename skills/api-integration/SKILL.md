---
name: api-integration
description: "Use when working with REST/GraphQL APIs, webhooks, API testing, authentication, rate limiting, OAuth 2.0, JWT tokens, API keys, bearer tokens, basic auth, API gateway, API documentation, OpenAPI/Swagger, Postman, curl, Python requests, Node.js fetch, axios, HTTP methods (GET, POST, PUT, PATCH, DELETE), request/response handling, error handling, retry logic, circuit breaker, pagination, cursor-based pagination, offset pagination, rate limit handling, backoff strategies, API versioning, content negotiation, JSON parsing, XML parsing, multipart form data, file uploads, download management, streaming responses, Server-Sent Events, WebSocket connections, gRPC, Protocol Buffers, webhook validation, webhook signing, HMAC verification, API monitoring, API analytics, API security, CORS, CSRF protection, input validation, output sanitization, API mocking, service integration, GitHub API, Stripe API, SendGrid API, Twilio API, AWS SDK, Google Cloud SDK, Azure SDK, or any external service integr..."
---



# API Integration Skill — REST/GraphQL/Webhook Communication

## Keywords
`rest api` `graphql` `webhook` `api testing` `authentication` `rate limiting` `oauth 2.0`
`jwt` `api key` `bearer token` `basic auth` `api gateway` `openapi` `swagger` `postman`
`curl` `python requests` `node fetch` `axios` `http methods` `get` `post` `put` `patch`
`delete` `error handling` `retry logic` `circuit breaker` `pagination` `cursor pagination`
`rate limit` `backoff` `api versioning` `content negotiation` `json` `xml` `multipart`
`file upload` `download` `streaming` `server-sent events` `websocket` `grpc` `protobuf`
`webhook validation` `hmac` `api monitoring` `api security` `cors` `csrf` `input validation`
`api mocking` `github api` `stripe api` `sendgrid` `twilio` `aws sdk` `google cloud`
`azure sdk` `service integration` `external service` `http client` `http request`
`http response` `status code` `header` `query parameter` `path parameter` `request body`
`response body` `timeout` `connection pool` `session management` `cookie` `redirect`
`user agent` `accept header` `content type` `authorization header`

## REST API Testing

### curl Examples

#### GET Request
```bash
# Basic GET
curl https://api.example.com/resource

# With headers
curl -H "Authorization: Bearer TOKEN" \
     -H "Content-Type: application/json" \
     https://api.example.com/resource

# With query parameters
curl "https://api.example.com/resource?key=value&limit=10"

# Pretty print JSON
curl -s https://api.example.com/resource | python3 -m json.tool

# Follow redirects
curl -L https://api.example.com/resource

# Verbose output
curl -v https://api.example.com/resource

# Save to file
curl -o output.json https://api.example.com/resource
```

#### POST Request
```bash
# JSON body
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"key": "value"}' \
     https://api.example.com/resource

# Form data
curl -X POST \
     -d "field1=value1&field2=value2" \
     https://api.example.com/resource

# File upload
curl -X POST \
     -F "file=@/path/to/file.pdf" \
     https://api.example.com/upload

# Multiple files
curl -X POST \
     -F "file1=@/path/to/file1.pdf" \
     -F "file2=@/path/to/file2.pdf" \
     https://api.example.com/upload
```

#### PUT/PATCH/DELETE
```bash
# PUT
curl -X PUT \
     -H "Content-Type: application/json" \
     -d '{"key": "updated_value"}' \
     https://api.example.com/resource/123

# PATCH
curl -X PATCH \
     -H "Content-Type: application/json" \
     -d '{"key": "partial_update"}' \
     https://api.example.com/resource/123

# DELETE
curl -X DELETE https://api.example.com/resource/123
```

### Python requests

#### GET Request
```python
import requests

# Basic GET
response = requests.get("https://api.example.com/resource")
print(response.json())

# With headers
headers = {
    "Authorization": "Bearer TOKEN",
    "Content-Type": "application/json"
}
response = requests.get("https://api.example.com/resource", headers=headers)

# With query params
params = {"key": "value", "limit": 10}
response = requests.get("https://api.example.com/resource", params=params)

# With timeout
response = requests.get("https://api.example.com/resource", timeout=30)
```

#### POST Request
```python
import requests

# JSON body
data = {"key": "value"}
response = requests.post("https://api.example.com/resource", json=data)
print(response.json())

# Form data
form_data = {"field1": "value1", "field2": "value2"}
response = requests.post("https://api.example.com/resource", data=form_data)

# File upload
files = {"file": open("/path/to/file.pdf", "rb")}
response = requests.post("https://api.example.com/upload", files=files)
```

#### Error Handling
```python
import requests

try:
    response = requests.get("https://api.example.com/resource")
    response.raise_for_status()
    data = response.json()
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
    print(f"Status Code: {e.response.status_code}")
    print(f"Response: {e.response.text}")
except requests.exceptions.ConnectionError as e:
    print(f"Connection Error: {e}")
except requests.exceptions.Timeout as e:
    print(f"Timeout Error: {e}")
except requests.exceptions.RequestException as e:
    print(f"Request Error: {e}")
```

### Node.js fetch

#### GET Request
```javascript
// Basic GET
const response = await fetch("https://api.example.com/resource");
const data = await response.json();
console.log(data);

// With headers
const response = await fetch("https://api.example.com/resource", {
  headers: {
    "Authorization": "Bearer TOKEN",
    "Content-Type": "application/json"
  }
});
```

#### POST Request
```javascript
// JSON body
const response = await fetch("https://api.example.com/resource", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({ key: "value" })
});
const data = await response.json();
```

## Authentication

### API Key
```bash
# Header
curl -H "X-API-Key: YOUR_API_KEY" https://api.example.com/resource

# Query parameter
curl "https://api.example.com/resource?api_key=YOUR_API_KEY"
```

### Bearer Token
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" https://api.example.com/resource
```

### OAuth 2.0
```bash
# Get access token
curl -X POST \
     -d "grant_type=client_credentials&client_id=YOUR_ID&client_secret=YOUR_SECRET" \
     https://api.example.com/oauth/token

# Use token
curl -H "Authorization: Bearer ACCESS_TOKEN" https://api.example.com/resource
```

### Basic Auth
```bash
curl -u username:password https://api.example.com/resource
```

### JWT
```python
import jwt
import time

# Create JWT
payload = {
    "user_id": 123,
    "exp": int(time.time()) + 3600
}
token = jwt.encode(payload, "secret", algorithm="HS256")

# Use token
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("https://api.example.com/resource", headers=headers)
```

## GraphQL

### Query
```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"query": "{ users { id name email } }"}' \
     https://api.example.com/graphql
```

### Mutation
```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"query": "mutation { createUser(name: \"John\", email: \"john@example.com\") { id name } }"}' \
     https://api.example.com/graphql
```

### Python
```python
import requests

query = """
query {
    users {
        id
        name
        email
    }
}
"""

response = requests.post(
    "https://api.example.com/graphql",
    json={"query": query},
    headers={"Authorization": "Bearer TOKEN"}
)
data = response.json()
```

## Webhooks

### Receiving Webhooks
```python
from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    # Verify signature
    signature = request.headers.get("X-Webhook-Signature")
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        request.data,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected):
        return jsonify({"error": "Invalid signature"}), 401
    
    payload = request.json
    event = payload.get("event")
    
    if event == "order.created":
        process_order(payload["data"])
    elif event == "payment.received":
        process_payment(payload["data"])
    
    return jsonify({"status": "received"}), 200
```

### Sending Webhooks
```python
import requests
import hmac
import hashlib
import json

def send_webhook(url, data, secret):
    payload = json.dumps(data)
    signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    response = requests.post(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature
        }
    )
    return response.status_code == 200
```

## Rate Limiting

### Handling Rate Limits
```python
import time
import requests

def make_request_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url)
        
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            time.sleep(retry_after)
            continue
        
        response.raise_for_status()
        return response.json()
    
    raise Exception("Max retries exceeded")
```

### Rate Limit Headers
```python
def check_rate_limit(response):
    remaining = response.headers.get("X-RateLimit-Remaining")
    limit = response.headers.get("X-RateLimit-Limit")
    reset = response.headers.get("X-RateLimit-Reset")
    
    print(f"Remaining: {remaining}/{limit}")
    print(f"Resets at: {reset}")
```

## API Testing

### Pytest API Tests
```python
import pytest
import requests

BASE_URL = "https://api.example.com"

def test_get_users():
    response = requests.get(f"{BASE_URL}/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_create_user():
    user = {"name": "Test User", "email": "test@example.com"}
    response = requests.post(f"{BASE_URL}/users", json=user)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == user["name"]
```

## Service Integration

### GitHub API
```python
import requests

headers = {
    "Authorization": "token YOUR_GITHUB_TOKEN",
    "Accept": "application/vnd.github.v3+json"
}

# List repos
response = requests.get("https://api.github.com/user/repos", headers=headers)

# Create issue
issue = {"title": "Bug Report", "body": "Description..."}
response = requests.post(
    "https://api.github.com/repos/owner/repo/issues",
    json=issue,
    headers=headers
)
```

### Stripe API
```python
import requests

headers = {
    "Authorization": "Bearer sk_test_YOUR_KEY",
    "Content-Type": "application/x-www-form-urlencoded"
}

# Create charge
data = {
    "amount": 2000,
    "currency": "usd",
    "source": "tok_visa"
}
response = requests.post(
    "https://api.stripe.com/v1/charges",
    data=data,
    headers=headers
)
```

## Integration

### With Quantum Nexus
- API key management via vault
- Service health monitoring
- Webhook handling

### With Aspen Grove
- Connector API integration
- Service synchronization
- Authentication management

### With Docker
- Container health checks
- Service deployment
- API gateway setup
