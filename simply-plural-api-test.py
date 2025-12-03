import requests

url = "https://api.apparyllis.com/v1/user/analytics"

payload = {}
headers = {
  'Accept': 'application/json',
  'Authorization': '<Authorization>'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
