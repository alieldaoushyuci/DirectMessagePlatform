IMPORTANT TO READ BEFORE YOU START:

How to use the application:
This works online and offline. However, if you want to message with another user, the server needs to be up, by running the file server.py. After that run a4.py which will pop up the application, from there you can actually communicate and add contacts. You can also just start up the a4.py alone without server.py running if you want to operate locally and look at your messages with other users. 


In the following I have a breakdown of every file in this zip file: 

ds_protocol.py:
Defines the communication protocol for interacting with the server, including functions to format JSON messages for user authentication, creating/sending posts, and handling direct messages. Contains utility functions for extracting data from server responses and validating messages.

test_dsmessage.py:
Contains test cases for the DirectMessage class, verifying message object creation and property handling.

ds_messenger.py:
Implements the DirectMessenger class that handles communication with a messaging server, including sending messages, retrieving new messages, and retrieving all messages. Creates socket connections to the server, handles authentication, and converts server responses into DirectMessage objects.

test_dsmessenger.py:
Contains test cases for the DirectMessenger class, testing server communication, message sending and retrieval functionality.

gui.py:
Contains the graphical user interface for a direct messaging application using Tkinter, with classes for the main application window, message display, and dialogs for adding contacts and configuring server settings. Handles user interactions, message display, and local/server message storage with Profile integration.

server.py: 
Contains the application - code linking. Assigns actions to each of the buttons and widgets in the applications and lets the user actually use the app. 