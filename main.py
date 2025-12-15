# === packages ===


import requests
from websockets.sync.client import connect
from difflib import SequenceMatcher
import jellyfish


# === keys ===
cipher_suite = open("fernet-key.txt").read().strip()
sp_key = open("api-key.txt").read().strip().split("\n")


# === values == 
all_alters = open("stored-data/alters.txt").read().strip().split("\n") #note whos system? [alter, system]


# === functions ===

# --- similarity ---

def compare_strings (str1, str2):
    "compares two strings and returns the similarity as a number from 0-1"
    s = SequenceMatcher(None, str1, str2)
    return s.ratio()

def compare_strings_2 (str1, str2):
    "other version of comparing strings. it has a weird output number, closer to 1 is best i think"
    return jellyfish.levenshtein_distance(str1,str2)

# --- sp ---
def get_sys_trait(sp_token,trait):
    "sp_token is the token, trait is an aspect like uid, username, desc, isAsystem. it returns a string of the trait"
    url = "https://api.apparyllis.com/v1/me/"
    payload = {}
    headers = {'Authorization': sp_token}
    response1 = requests.request("GET", url, headers=headers, data=payload)
    return response1.json()["content"][trait]
    
def get_sp_trait_for_all_fronters(sp_token,trait):
    "sp_token is the token, and the trait is the desired aspect i.e. id,member,etc. it returns a list of strings of traits"
    url = "https://api.apparyllis.com/v1/fronters/"
    payload = {}
    headers = {'Authorization': sp_token}
    response1 = requests.request("GET", url1, headers=headers, data=payload)
    trait_lst = []
    for alter in response1.json():
        trait_lst.append(alter["content"][trait])
    return trait_lst
    
def get_all_fronters(sp_token):
    "gets everyone in front for a given sp_token"
    sysID = get_sys_trait(sp_token, "uid")
    memID = get_sp_trait_for_all_fronters(sp_token, "member")
    fronters = []
    for fronter in range(len(memID)):
        url2 = "https://api.apparyllis.com/v1/member/" + sysID[fronter] + "/" + memID[fronter]
        response2 = requests.request("GET", url2, headers=headers, data=payload)
        fronters.append(response2.json()["content"]["name"])
    return fronters

def get_attribute_for_all_alters(sp_token,trait):
    "sp_token is the token, and the trait is the desired aspect.  it returns a list of strings of traits"
    #trait options are: name, buckets, color, desc, pronouns, archived, preventsFrontNotifs
    sysID = get_sys_trait(sp_token, "uid")
    url = "https://api.apparyllis.com/v1/members/"+sysID
    payload = {}
    headers = {'Authorization': sp_token}
    response = requests.request("GET", url, headers=headers, data=payload)
    traits = []
    for alter in response.json():
        traits.append(alter["content"][trait])
    return traits


def determine_queried_alter(alters, query,threshold=0.8,n=3):
    "given a query, guesses the most likely alter. if none are very likely, returns a list of the top n"
    probs = list(map(lambda x: compare_strings(x,query), alters))
    best_guess = alters[probs.index(max(probs))]
    if best_guess >= threshold:
        return best_guess
    else:
        return sorted(zip(probs, alters), reverse=True)[:n]
    
# --- encrypt ---

def encrypt_and_add__token(token):
    return token
    #with open("api-key.txt", "a") as f:
    #    print(encrypted_token)
    #    f.write(encrypted_token)
    #    f.write("\n")
    

    
# === socket ===
# wip! not sure what package to use, all i know is for typescript you use ws
def initiate_socket(sp_token):
    with connect("wss://api.apparyllis.com/v1/socket") as websocket:
        headers = {'Authorization': sp_token}
        payload = {}
        websocket.send(requests.request("GET", url1, headers=headers, data=payload))
        message = websocket.recv()
        print(message)
        


# === setup ===
# --- get alters ---
def get_all_alters(sp_token):
    sysID = get_sys_trait(sp_token, "uid")
    url = "https://api.apparyllis.com/v1/members/"+sysID
    payload = {}
    headers = {'Authorization': sp_token}
    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.text)

# === main ===
        
print(get_all_fronters(sp_key[0]))
#encrypt_and_add__token(sp_key)


# === notes ===
## right now there is ZERO multithreading, only one person can talk to the bot at a time
