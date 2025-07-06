# import requests

# url = "https://dc97-188-48-112-197.ngrok-free.app"
# data = {
#     "message": "Do I have any quizzes next week?"
# }

# res = requests.post(url, json=data)

# print("Status:", res.status_code)
# print("Response:", res.json())

import requests

url = "https://ccf1-188-48-112-197.ngrok-free.app/chat/"
data = {
    "message": "Do I have any quizzes next week?"
}

response = requests.post(url, json=data)
print(response.json())

