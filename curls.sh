# Shell script to test the flight booking API

# Login as user1 and store token
export TOKEN1=$(curl -s -X POST "http://localhost:8000/users/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "default@default.com", "password": "default@default.com"}' | jq -r .token.access_token)
echo "User1 token: $TOKEN1"

# send message to the chatbot
curl -X POST "http://localhost:8000/chat" -Ss \
  -H "Authorization: Bearer $TOKEN1" \
  -H "Content-Type: application/json" \
  -d '{"content": "What are the available flights from New York to San Francisco?"}' | jq .

# ask to the chatbot about the last message
curl -X POST "http://localhost:8000/chat" -Ss \
  -H "Authorization: Bearer $TOKEN1" \
  -H "Content-Type: application/json" \
  -d '{"content": "What was the last message?"}' | jq .

# get chat history
curl -X GET "http://localhost:8000/chat/history" -Ss \
  -H "Authorization: Bearer $TOKEN1" \
  -H "Content-Type: application/json" | jq .

# clear chat history
curl -X DELETE "http://localhost:8000/chat/history" -Ss \
  -H "Authorization: Bearer $TOKEN1" \
  -H "Content-Type: application/json" | jq .