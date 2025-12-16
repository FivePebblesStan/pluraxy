# === packages ===
import requests
from websockets.sync.client import connect
from difflib import SequenceMatcher
import jellyfish
from vigenere import encrypt, decrypt, random_key\


# === keys ===
cipher_suite = open("fernet-key.txt").read().strip()
sp_key = open("api-key.txt").read().strip().split("\n")


# === values == 
all_alters = open("stored-data/alters.txt").read().strip().split("\n") #note whos system? [alter, system]
payload = {}


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
    headers = {'Authorization': sp_token}
    response1 = requests.request("GET", url, headers=headers, data=payload)
    return response1.json()["content"][trait]
    
def get_sp_trait_for_all_fronters(sp_token,trait):
    "sp_token is the token, and the trait is the desired aspect i.e. id,member,etc. it returns a list of strings of traits"
    url = "https://api.apparyllis.com/v1/fronters/"
    
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

# TODO: query alter

# TODO: get a message
# note who its from and who its to
# store all of that and encrypt it all
    
# --- encrypt ---
def encrypt_and_add_message(message):
    cipher_key = open("vigenere.txt").read().strip()
    cipher_message = encrypt(message, cipher_key)
#   decrypt(cipher, cipher_key)
    with open("queued-messages.txt", "a") as f:
        print(cipher_message)
        f.write(cipher_message)
        f.write("\n")
    return message

    
# === socket ===
# wip! not sure what package to use, all i know is for typescript you use ws
def initiate_socket(sp_token):
    with connect("wss://api.apparyllis.com/v1/socket") as websocket:
        headers = {'Authorization': sp_token}
        websocket.send(requests.request("GET", url1, headers=headers, data=payload))
        message = websocket.recv()
        print(message)
        
# TODO: SOCKETS

# === setup ===
# --- get alters ---
def choose_bucket(sp_token, alter_name):
    "cmon. you know what sp_token is. alter_name is the name of an alter that has the bucket you want "
    name_buckets = list(map(lambda x: get_attribute_for_all_alters(sp_token,x),["name","buckets"]))
    messy_bucket = [a[1] if a[0] == alter_name else None for a in zip(name_buckets[0],name_buckets[1])]
    bucket = next(val for val in messy_bucket if val is not None)[0]
    return bucket

def get_all_alters_in_bucket(sp_token, bucket, archived=False):
    "gets all alters from whatever bucket you want to get alters from, including archived ones if archived=true"
    # nab = name_archived_buckets
    nab = list(map(lambda x: get_attribute_for_all_alters(sp_token,x), ["name","archived","buckets"]))
    if not archived:
        name_buckets_unfiltered = [[a[0],a[2]] if a[1] == False else None for a in zip(nab[0], nab[1], nab[2])]
        name_buckets = list(filter(lambda a: a != None, name_buckets_unfiltered))
    else:
        name_buckets = [[a[0],a[2]] for a in zip(nab[0], nab[1], nab[2])]
    alters=[]
    for alter in name_buckets:
        if alter[1] == []:
            continue
        elif alter[1][0] == bucket:
            alters.append(alter[0])
    return alters

def write_alters_to_file(sp_token, alters, username):
    "writes a list of all alters to file, given a list of strings of names of alters, and a sp username"
    username = get_sys_trait(sp_token,"username")
    if username not in open("stored-data/users.txt").read():
        with open("stored-data/alters.txt", "a") as f:
            for alter in alters:
                f.write(alter+","+username+"\n")
        with open("stored-data/users.txt", "a") as f:
            f.write(username+"\n")
# TODO: UPDATE ALTERS IN FILE
            

# === main ===     
print(get_all_fronters(sp_key[0]))
#encrypt_and_add__token(sp_key)
write_alters_to_file(sp_key[0],get_all_alters_in_bucket(sp_key[0],choose_bucket(sp_key[0],"Siffrin")),get_sys_trait(sp_key[0],"username"))

# === notes ===
## todos:
# right now there is ZERO multithreading, only one person can talk to the bot at a time
