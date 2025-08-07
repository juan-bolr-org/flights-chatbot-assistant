#!/bin/bash

# Test script to check the chat sessions endpoint
echo "Testing chat sessions API..."

# Check if API is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "API is not running. Please start the API first."
    exit 1
fi

# First, let's get a token (login with default user)
echo "Getting authentication token..."
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "default@default.com", "password": "password123"}')

if [ $? -ne 0 ]; then
    echo "Failed to login. Make sure the API is running and the default user exists."
    exit 1
fi

# Extract the access token
ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access_token')

if [ "$ACCESS_TOKEN" = "null" ] || [ -z "$ACCESS_TOKEN" ]; then
    echo "Failed to get access token. Response: $TOKEN_RESPONSE"
    exit 1
fi

echo "Got access token successfully"

# Test getting chat sessions
echo "Testing chat sessions endpoint..."
SESSIONS_RESPONSE=$(curl -s -X GET http://localhost:8000/api/chat/sessions \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Sessions response: $SESSIONS_RESPONSE"

# Test sending a chat message to create a session
echo "Sending a test chat message..."
CHAT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{"content": "Hello, can you help me find flights?", "session_id": "test_session_123"}')

echo "Chat response: $CHAT_RESPONSE"

# Test getting sessions again
echo "Testing chat sessions endpoint after sending message..."
SESSIONS_RESPONSE_2=$(curl -s -X GET http://localhost:8000/api/chat/sessions \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Sessions response after chat: $SESSIONS_RESPONSE_2"

echo "Test completed!"
