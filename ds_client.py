# Starter code for assignment 3 in ICS 32 Programming with Software Libraries in Python

# Replace the following placeholders with your information.

# Ali Eldaoushy
# eldaousa@uci.edu
# 74614851
import socket
import json
import time
from ds_protocol import *
FORMAT = 'utf-8'

def send(server:str, port:int, username:str, password:str, message:str=None, bio:str=None) -> bool:
  try: 
    #Establish conncetion to server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server, port))

    #Send join message
    join_message = create_join_message(username, password)
    client_socket.sendall(join_message.encode(FORMAT))

    #Get response
    response = recv_response(client_socket)

    
    #Deserialize the response
    response = extract_json(response) # response is a JoinResponse object

    #Validate response
    if response.success == 'error':
      print('ERROR: unexpected response')
      return False
    
    #Print the response
    print_response(response)

    #Send Bio/Post if the user wants (Don't allow a blanks)
    if validate(bio):
      bio_message = make_bio(response.token, bio)
      client_socket.sendall(bio_message.encode(FORMAT))
    
    if validate(message):
      post_message = make_post(response.token, message)
      client_socket.sendall(post_message.encode(FORMAT))



    return True
  except Exception as error:
    print(f"ERROR: {error}")
    return False

