import socket
from ds_protocol import *
import time
from Profile import Profile
from pathlib import Path


class DirectMessage:
  def __init__(self):
    self.recipient = None
    self.sender = None
    self.message = None
    self.timestamp = None
     

class DirectMessenger:
  def __init__(self, dsuserver=None, username=None, password=None):
     self.dsuserver = dsuserver
     self.username = username
     self.password = password
     self.token = None

  def send(self, message:str, recipient:str) -> bool:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((self.dsuserver, 3001))
    print('client connected')

    join_msg = create_join_message(self.username, self.password)

    send_msg = client.makefile('w')
    recv = client.makefile('r')

    send_msg.write(join_msg + '\r\n')
    send_msg.flush()

    resp = recv.readline()
    resp = extract_dm(resp)
    self.token = resp['token']

    dm_msg = directmessage(self.token, message, recipient, time.time())

    send_msg.write(dm_msg + '\r\n')
    send_msg.flush()

    resp = recv.readline()
    resp = extract_dm(resp)


    if resp['type'] == 'error':
        print('ERROR')
        return False
        
    return True
  
		
  def retrieve_new(self) -> list:
    # must return a list of DirectMessage objects containing all new messages
    try:    
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.dsuserver, 3001))

        join_msg = create_join_message(self.username, self.password)

        send_msg = client.makefile('w')
        recv = client.makefile('r')

        send_msg.write(join_msg + '\r\n')
        send_msg.flush()

        resp = recv.readline()
        resp = extract_dm(resp)
        self.token = resp['token']
    
        unread_msg = request_newmessage(self.token)
        send_msg.write(unread_msg + '\r\n')
        send_msg.flush()

        resp = recv.readline()
        resp = extract_dm(resp)

        dm_list = []
        for messages in resp['messages']:
           dm = DirectMessage()
           dm.sender = messages['from']
           dm.message = messages['message']
           dm.timestamp = messages['timestamp']
           dm_list.append(dm)

        return dm_list

    except Exception as e:
       print('ERROR', e)
    
  def retrieve_all(self) -> list:
    # must return a list of DirectMessage objects containing all messages
    try:
      client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      client.connect((self.dsuserver, 3001))

      join_msg = create_join_message(self.username, self.password)

      send_msg = client.makefile('w')
      recv = client.makefile('r')

      send_msg.write(join_msg + '\r\n')
      send_msg.flush()

      resp = recv.readline()
      resp = extract_dm(resp)
      self.token = resp['token']
    
      all_msg = request_allmessages(self.token)
      send_msg.write(all_msg + '\r\n')
      send_msg.flush()

      resp = recv.readline()
      resp = extract_dm(resp)

      dm_list = []
      prof = Profile()
      user_file_name = '/Users/alieldaoushy/ICS32/assignment4/ali.dsu'
      prof.load_profile(user_file_name)
      for messages in resp['messages']:
        dm = DirectMessage()
        dm.message = messages['message']
        dm.timestamp = messages['timestamp']
        if 'recipient' in messages.keys():
           dm.recipient = messages['recipient']
           prof.messages.append({'recipient': dm.recipient, 'message': dm.message, 'timestamp': dm.timestamp})
           prof.save_profile(user_file_name)
        else:
           dm.sender = messages['from']
           prof.messages.append({'from': dm.sender, 'message': dm.message, 'timestamp': dm.timestamp})
           prof.save_profile(user_file_name)
        dm_list.append(dm)

      return dm_list
  
    except Exception as e:
       print('ERROR after try block', e)
  