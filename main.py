# === packages ===
import requests
from difflib import SequenceMatcher
import jellyfish
from vigenere import encrypt, decrypt, random_key

import websocket
import _thread
import time
import rel
import pickle


# === keys ===
cipher_suite = open("fernet-key.txt").read().strip()
sp_key = open("api-key.txt").read().strip().split("\n") #associate keys with discord users

# === values == 
all_alters = list(map(lambda x:x.split(","), open("stored-data/alters.txt").read().strip().split("\n")))
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
    response1 = requests.request("GET", url, headers=headers, data=payload)
    trait_lst = []
    for alter in response1.json():
        trait_lst.append(alter["content"][trait])
    return trait_lst

def get_all_fronters(sp_token):
    "gets everyone in front for a given sp_token"
    sysID = get_sys_trait(sp_token, "uid")
    memID = get_sp_trait_for_all_fronters(sp_token, "member")
    headers = {'Authorization': sp_token}
    fronters = []
    for fronter in range(len(memID)):
        url2 = "https://api.apparyllis.com/v1/member/" + sysID + "/" + memID[fronter]
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

def determine_queried_option(options, query,threshold=0.8,n=3):
    "given a query, guesses the most likely option from list. if none are very likely, returns a list of the top n"
    probs = list(map(lambda x: float(compare_strings(x,query)), options))
    best_guess = max(probs)
    best_guess_name = options[probs.index(max(probs))]
    if best_guess >= threshold:
        return best_guess_name
    else:
        return sorted(zip(probs, options), reverse=True)[:n]

# TODO: query alter

# TODO: get a message
# note who its from and who its to
# store all of that and encrypt it all
    
# --- encrypt ---
def encrypt_and_add_message(message, alter,username):
    cipher_key = open("vigenere.txt").read().strip()
    cipher_message = encrypt(message+","+str(alter)+","+username, cipher_key)
#   decrypt(cipher, cipher_key)
    with open("queued-messages.txt", "a") as f:
        print(cipher_message)
        f.write(cipher_message)
        f.write("\n")
    return message

    
# === socket ===
def on_message(ws, message):
    print(message, "msg!")

def on_error(ws, error):
    print(error, "err :c")

def on_close(ws, close_status_code, close_msg):
    print("### closed socket ###")

def initiate_socket(sp_token):
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://api.apparyllis.com/v1/socket",
                              on_open=lambda x: x.send(pickle.dumps({'op': 'authenticate', 'token': sp_token})),
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    ws.run_forever(dispatcher=rel, reconnect=5)  # automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()
    return ws

def keep_socket_open (ws):
    #async it :D
    if time.time() % 10 == 0:
        ws.send("ping")
    
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
# TODO: UPDATE ALTERS IN FILE, UPDATE ALL_ALTERS
            

# === main ===
def add_new_message(sp_token_from_user): #note! there are some generalizable frameworks here
    # "you want to send a message? lovely! to which system?" [asterisms]
    query_system = str(input("you want to send a queued message? lovely! to which system? (enter their simplyplural username) "))
    print("...checking if theyre registered with pluraxy...")
    guess_target_system = determine_queried_option(open("stored-data/users.txt").read().strip().split("\n"),query_system)
    if type(guess_target_system) == type([]):
        all_guesses = ["\033[1m"+str(1+val)+"\033[0m: "+"prob. "+str(round(guess[0],2))+", name. "+guess[1] for val,guess in zip(range(len(guess_target_system)),guess_target_system)]
        try: 
            which_system = int(input("which system did you want?\n" + "\n".join(all_guesses) + "\nrespond with a number "))
        except:
            raise ValueError("Please respond with a number.")
        target_system = guess_target_system[which_system-1][1]
    else:
        target_system = guess_target_system
    # "...checking if theyre registered.....found them! which member?" [sif]
    query_alter = str(input("...found them! which member in their system did you want to message? "))
    possible_alters = list(filter(lambda x:x!=None, [alter[0] if alter[1]==target_system else None for alter in all_alters]))
    #list(filter(lambda x: x[1]==target_system,all_alters))
    print(possible_alters)
    guess_target_alter = determine_queried_option(possible_alters,query_alter)
    if type(guess_target_alter) == type([]):
        print(guess_target_alter)
        all_guesses = ["\033[1m"+str(1+val)+"\033[0m: "+"prob. "+str(round(guess[0],2))+", name. "+guess[1][0] for val,guess in zip(range(len(guess_target_alter)),guess_target_alter)]
        try:
# "...checking if theyre in the system.....did you mean: 1: 'Siffrin' 2: 'Seamstress' 3: 'Songbird'? type a number to respond" [1]
            which_alter = int(input("which alter did you want?\n" + "\n".join(all_guesses) + "\nrespond with a number "))
        except:
            raise ValueError("Please respond with a number.")
        target_alter = guess_target_alter[which_alter-1][1]
    else:
        target_alter = guess_target_alter
        query_message = str(input("lovely! what message do you want to pass on for when they front? "))
    # "lovely! what message do you want to pass on for when they front?" ["mrow!!"]
    fronter_s = get_all_fronters(sp_token_from_user)
    if len(fronter_s) != 1:
    # "want this to be sent from 1. everyone in front  2. fronter A 3. fronter B .... type a number, or combination of numbers (to send label it as from all of them) to respond" [1]
        all_fronters = list(map(lambda x:list(x),list(zip(fronter_s,list(map(lambda x:str(x+2),list(range(len(fronter_s)))))))))
        all_fronters_str = list(map(lambda x: x[1]+": "+x[0],all_fronters))
        try:
            which_alter = str(input("which fronter did you want to send the message from?\n1: All fronters\n" +"\n".join(all_fronters_str) + "\nrespond with a number "))
            if which_alter == "1":
                fronter_message = fronter_s
            else:
                fronter_message = []
                for alter_option in list(which_alter):
                    fronter_message.append(fronter_s[int(alter_option)-2])
        except:
            raise ValueError("Please respond with a number.")
    else:
         # "this will be sent from [whos in front in your system]" OR
        fronter_message = fronter_s[0]
        print("this message will be sent from " + fronter_message)
    
    users_username = get_sys_trait(sp_token_from_user,"username")
    # "message logged and queued! thank you for using pluraxy :D"
    encrypt_and_add_message(query_message,fronter_message,users_username)
    print("message logged and queued! thank you for using pluraxy :D")
    return True
    
print(get_all_fronters(sp_key[0]))
#write_alters_to_file(sp_key[0],get_all_alters_in_bucket(sp_key[0],choose_bucket(sp_key[0],"Siffrin")),get_sys_trait(sp_key[0],"username"))

# === notes ===
## todos:
# right now there is ZERO multithreading, only one person can talk to the bot at a time
# pluralkit api integration
# slash commands
# delete query
