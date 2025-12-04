import requests

api_key = open("api-key.txt").read()

url1 = "https://api.apparyllis.com/v1/fronters/"

payload = {}
headers = {
  'Authorization': api_key
}

response1 = requests.request("GET", url1, headers=headers, data=payload)

sysID = response1.json()[0]["content"]["uid"]
memID1 = response1.json()[0]["content"]["member"]

url2 = "https://api.apparyllis.com/v1/member/" + sysID + "/" + memID1

response2 = requests.request("GET", url2, headers=headers, data=payload)

fronter = response2.json()["content"]["name"]

print(fronter)
