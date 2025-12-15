import requests

api_key = open("api-key.txt").read().strip()
def get_all_fronters(api_key):
    url1 = "https://api.apparyllis.com/v1/fronters/"
    payload = {}
    headers = {'Authorization': api_key}
    response1 = requests.request("GET", url1, headers=headers, data=payload)
    print(response1.json())
    sysID,memID = [],[]
    for alter in response1.json():
        sysID.append(alter["content"]["uid"])
        memID.append(alter["content"]["member"])
    fronters = []
    for fronter in range(len(sysID)):
        url2 = "https://api.apparyllis.com/v1/member/" + sysID[fronter] + "/" + memID[fronter]
        response2 = requests.request("GET", url2, headers=headers, data=payload)
        fronters.append(response2.json()["content"]["name"])
    return fronters

print(get_all_fronters(api_key))

