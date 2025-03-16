# ds_protocol.py

# Starter code for assignment 3 in ICS 32 Programming with Software Libraries in Python

# Replace the following placeholders with your information.

# Ali Eldaoushy
# eldaousa@uci.edu
# 74614851

import json
import socket
import time
from collections import namedtuple
from Profile import Post

FORMAT = 'utf-8'


class DSProtocolError(Exception):
  """ A Base Error Message for exceptions in the DSProtocol module """
  pass 
# Namedtuple to hold the values retrieved from json messages.
JoinResponse = namedtuple('JoinResponse', ['success','message','token'])

def extract_json(json_msg: str) -> JoinResponse:
    '''
    Call the json.loads function on a json string and convert it to a DataTuple object
    '''
    try:
        json_obj = json.loads(json_msg)
        success = json_obj.get('response', {}).get('type', None)
        message = json_obj.get('response', {}).get('message', None)
        token = json_obj.get('response', {}).get('token', None)
        return JoinResponse(success, message, token)
    except (json.JSONDecodeError, TypeError):
        return JoinResponse(None, None, None)




def create_join_message(username:str, password:str, token:str=None) -> str:
  """ Create a join message in json format """
  msg = json.dumps({"join":{"username": username,"password": password, "token":""}})

  return msg

def make_bio(token:str, bio:str) -> str:
  """ format a bio to send """
  post = Post(entry = bio)
  msg = {
    "token": token,
    "bio": {
      "entry" : post.entry, 
      "timestamp" : time.time(),
    }
  }
  return json.dumps(msg)


def make_post(token:str, message:str) -> str:
  """ format a post to send """
  post = Post(entry = message)
  msg = {
    "token": token,
    "post": {
      "entry" : post.entry, 
      "timestamp" : time.time(),
    }
  }
  return json.dumps(msg)


def recv_response(socket: socket.socket) -> str:
    """ Receive a response from the server.
        1024 is max bits to receive.
        FORMAT is utf-8.
    """
    try:
        response = socket.recv(1024).decode(FORMAT).strip()
        return response if response else ""
    except (OSError, ConnectionError):
        return ""


def print_response(response: JoinResponse) -> None:
  print(f"Success: {response.success}")
  print(f"Message: {response.message}")
  print(f"Token: {response.token}")

def validate(message):
  if message is None or message == '':
    return False
  return True

def directmessage(token : str, message : str, recipient : str, timestamp : str):
  dm_msg = json.dumps({"token": token, "directmessage": {'entry' : message, 'recipient' : recipient, 'timestamp': timestamp}})
  return dm_msg

def request_newmessage(token : str):
  new_msg = json.dumps({"token" : token, "directmessage" : 'new'})
  return new_msg

def request_allmessages(token : str):
  all_msg = json.dumps({"token" : token, "directmessage" : 'all'})
  return all_msg

def extract_dm(json_msg: str) -> dict:
    try:
        if json_msg is None or json_msg == "":
            return None
        json_dict = json.loads(json_msg)
        return json_dict.get('response', {})
    except json.JSONDecodeError:
        print("Json cannot be decoded.")
        return None
  
def create_dm_request(token: str, username: str, password : str):
  """ Create a direct message request in json format """
  dm_request = json.dumps({'join' : {'username' : username, 'password' : password, 'token' : token}})
  return dm_request
