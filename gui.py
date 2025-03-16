import tkinter as tk
from tkinter import ttk, filedialog
from typing import Text
from ds_messenger import DirectMessenger, DirectMessage
from ds_protocol import *
import json
from Profile import Profile
from pathlib import Path


class Body(tk.Frame):
    def __init__(self, root, recipient_selected_callback=None):
        tk.Frame.__init__(self, root)
        self.root = root
        self._contacts = [str]
        self._select_callback = recipient_selected_callback
        # After all initialization is complete,
        # call the _draw method to pack the widgets
        # into the Body instance
        self._draw()

    def node_select(self, event):
        index = int(self.posts_tree.selection()[0])
        entry = self._contacts[index]
        if self._select_callback is not None:
            self._select_callback(entry)

    def insert_contact(self, contact: str):
        self._contacts.append(contact)
        id = len(self._contacts) - 1
        self._insert_contact_tree(id, contact)

    def _insert_contact_tree(self, id, contact: str):
        if len(contact) > 25:
            entry = contact[:24] + "..."
        id = self.posts_tree.insert('', id, id, text=contact)

    def insert_user_message(self, message: str):
        self.entry_editor.insert(tk.END, message + '\n', 'entry-right')

    def insert_contact_message(self, message: str):
        self.entry_editor.insert(tk.END, message + '\n', 'entry-left')

    def get_text_entry(self) -> str:
        return self.message_editor.get('1.0', 'end').rstrip()

    def set_text_entry(self, text: str):
        self.message_editor.delete(1.0, tk.END)
        self.message_editor.insert(1.0, text)

    def _draw(self):
        posts_frame = tk.Frame(master=self, width=250)
        posts_frame.pack(fill=tk.BOTH, side=tk.LEFT)

        self.posts_tree = ttk.Treeview(posts_frame)
        self.posts_tree.bind("<<TreeviewSelect>>", self.node_select)
        self.posts_tree.pack(fill=tk.BOTH, side=tk.TOP,
                             expand=True, padx=5, pady=5)

        entry_frame = tk.Frame(master=self, bg="")
        entry_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)

        editor_frame = tk.Frame(master=entry_frame, bg="red")
        editor_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        scroll_frame = tk.Frame(master=entry_frame, bg="blue", width=10)
        scroll_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=False)

        message_frame = tk.Frame(master=self, bg="yellow")
        message_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=False)

        self.message_editor = tk.Text(message_frame, width=0, height=5)
        self.message_editor.pack(fill=tk.BOTH, side=tk.LEFT,
                                 expand=True, padx=0, pady=0)

        self.entry_editor = tk.Text(editor_frame, width=0, height=5)
        self.entry_editor.tag_configure('entry-right', justify='right')
        self.entry_editor.tag_configure('entry-left', justify='left')
        self.entry_editor.pack(fill=tk.BOTH, side=tk.LEFT,
                               expand=True, padx=0, pady=0)

        entry_editor_scrollbar = tk.Scrollbar(master=scroll_frame,
                                              command=self.entry_editor.yview)
        self.entry_editor['yscrollcommand'] = entry_editor_scrollbar.set
        entry_editor_scrollbar.pack(fill=tk.Y, side=tk.LEFT,
                                    expand=False, padx=0, pady=0)


class Footer(tk.Frame):
    def __init__(self, root, send_callback=None):
        tk.Frame.__init__(self, root)
        self.root = root
        self._send_callback = send_callback
        self._draw()

    def send_click(self):
        if self._send_callback is not None:
            self._send_callback()

    def _draw(self):
        save_button = tk.Button(master=self, text="Send", width=20,
                                command=self.send_click)
        save_button.pack(fill=tk.BOTH, side=tk.RIGHT, padx=5, pady=5)

        self.footer_label = tk.Label(master=self, text="Ready.")
        self.footer_label.pack(fill=tk.BOTH, side=tk.LEFT, padx=5)


class NewContactDialog(tk.simpledialog.Dialog):
    def __init__(self, root, title=None, user=None, pwd=None,
                 server=None, path=None):
        self.root = root
        self.server = server
        self.user = user
        self.pwd = pwd
        self.path = path
        self.login_successful = False  # Login Key
        super().__init__(root, title)

    def body(self, frame):
        self.path_label = tk.Label(frame, width=30, text="Filepath")
        self.path_label.pack()
        self.path_entry = tk.Entry(frame, width=30)
        self.path_entry.insert(tk.END, self.path)
        self.path_entry.pack()

        self.server_label = tk.Label(frame, width=30, text="DS Server Address")
        self.server_label.pack()
        self.server_entry = tk.Entry(frame, width=30)
        self.server_entry.insert(tk.END, self.server)
        self.server_entry.pack()

        self.username_label = tk.Label(frame, width=30, text="Username")
        self.username_label.pack()
        self.username_entry = tk.Entry(frame, width=30)
        self.username_entry.insert(tk.END, self.user)
        self.username_entry.pack()

        self.password_label = tk.Label(frame, width=30, text="Password")
        self.password_label.pack()
        self.password_entry = tk.Entry(frame, width=30)
        self.password_entry['show'] = '*'
        self.password_entry.insert(tk.END, self.pwd)
        self.password_entry.pack()

    def apply(self):
        self.user = self.username_entry.get()
        self.pwd = self.password_entry.get()
        self.server = self.server_entry.get()
        self.path = self.path_entry.get()

        # Ensure path ends with .dsu extension
        if not self.path.endswith('.dsu'):
            self.path = self.path + '.dsu'
            print(f"Added .dsu extension to path: {self.path}")

        filepath = Path(self.path)
        if filepath.exists():
            try:
                with open(self.path, 'r') as userinfo:
                    user = userinfo.readline()
                    user = json.loads(user)
                    entryusername = user['username']
                    entrypass = user['password']
                    self.user = self.username_entry.get().strip()
                    self.pwd = self.password_entry.get()
                    if self.user != entryusername:
                        print('Username incorrect')
                        self.login_successful = False
                    elif self.pwd != entrypass:
                        print('Incorrect Password')
                        self.login_successful = False
                    else:
                        print('Signed in')
                        self.login_successful = True
            except Exception as e:
                print(f"Error opening file: {e}")
                self.login_successful = False
        else:
            try:
                # Ensure parent directory exists
                filepath.parent.mkdir(parents=True, exist_ok=True)

                # Create an empty file first
                filepath.touch()

                # Then create and save the profile
                new_profile = Profile(self.server, self.user, self.pwd)
                new_profile.save_profile(self.path)
                print(f'New profile created at {self.path}')
                self.login_successful = True
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"Error creating profile: {e}")
                self.login_successful = False


class AddFriend(tk.simpledialog.Dialog):
    def __init__(self, root, title, contact):
        self.root = root
        self.contact = contact
        super().__init__(root, title)

    def body(self, frame):
        self.contact_label = tk.Label(frame, width=30, text='Add Friend')
        self.contact_label.pack()
        self.contact_entry = tk.Entry(frame, width=30)
        self.contact_entry.insert(tk.END, self.contact)
        self.contact_entry.pack()

    def apply(self):
        self.contact = self.contact_entry.get()


class MainApp(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root
        self.username = ''
        self.password = ''
        self.server = ''
        self.recipient = ''
        self.path = ''
        self._draw()

    def make_list(self):
        path_obj = Path(self.path)
        if path_obj.exists():
            try:
                user = Profile()
                user.load_profile(self.path)
                # Display all old messages between you and selected user
                for friend in user.friends:
                    self.body.insert_contact(friend)
            except Exception as e:
                print(f"Error loading profile: {e}")
        else:
            # Create a new profile if the file doesn't exist
            user = Profile(self.server, self.username, self.password)
            # Create parent directories if they don't exist
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            # Create the file
            path_obj.touch()
            # Save the new profile
            user.save_profile(self.path)
            print(f"Created new profile at {self.path}")

    def send_message(self):
        text_box_message = self.body.get_text_entry()
        if not text_box_message.strip():  # Don't send empty messages
            return

    # Save message to local profile regardless of server availability
        try:
            user_profile = Profile()
            user_profile.load_profile(self.path)
            # Add this message to the profile's messages
            timestamp = time.time()
            user_profile.messages.append({
                'recipient': self.recipient,
                'message': text_box_message,
                'timestamp': timestamp
            })
            user_profile.save_profile(self.path)

            # Show the message in the UI
            self.body.insert_user_message(f"You: {text_box_message}")
            self.body.set_text_entry("")

            # Try to send to server if available
            try:
                dm = DirectMessenger(self.server, self.username, self.password)
                result = dm.send(
                    message=text_box_message, recipient=self.recipient
                    )
                if result:
                    print("Message sent to server successfully")
                else:
                    print("Failed to send message to server")
            except Exception as e:
                print(f"Server unavailable: {e}. Message saved locally only.")
                self.footer.footer_label.config(text="Server unavailable.")

        except Exception as e:
            print(f"Error saving message to profile: {e}")

    def add_contact(self):
        ud = AddFriend(self.root, "Add Friend", self.recipient)
        contact = ud.contact
        self.body.insert_contact(contact)

        dsuserver = '127.0.0.1'
        password = 'friendpassword'

        # Use a consistent directory for friends but with dynamic user profile
        path = '/Users/alieldaoushy/ICS32/assignment4/'
        filename = 'friends.dsu'
        profile = Profile(dsuserver, contact, password)

        user = Profile()
        user.load_profile(self.path)

        user.friends.append(contact)
        profile.friends.append(self.username)
        userdm = DirectMessenger(self.server, self.username, self.password)

        filepath = Path(path) / Path(filename)
        if filepath.exists():
            profile.save_profile(str(filepath))
        else:
            filepath.touch()
            profile.save_profile(str(filepath))

        user.save_profile(self.path)  # Use the stored path for saving

    def recipient_selected(self, recipient):
        self.recipient = recipient
        # Clear current messages in the chat window
        self.body.entry_editor.delete(1.0, tk.END)
        # Display messages for this recipient
        self.display_chat()

    def configure_server(self):
        ud = NewContactDialog(self.root, "Configure Account", self.username,
                              self.password, self.server, self.path)

        # Check if login was successful using the flag
        if ud.login_successful:
            self.username = ud.user
            self.password = ud.pwd
            self.server = ud.server
            self.path = ud.path
            self.make_list()  # Only make list if login successful
            return True
        return False

    def publish(self, message: str):
        self.body.insert_user_message(f"You: {message}")
        self.body.set_text_entry("")

        # Save this message to the profile
        try:
            user_profile = Profile()
            user_profile.load_profile(self.path)
            # Add this message to the profile's messages
            timestamp = time.time()
            user_profile.messages.append({
                'recipient': self.recipient,
                'message': message,
                'timestamp': timestamp
            })
            user_profile.save_profile(self.path)
        except Exception as e:
            print(f"Error saving message to profile: {e}")

    def display_chat(self):
        try:
            # Load the current user's profile
            user_profile = Profile()
            user_profile.load_profile(self.path)

            # Try to get messages from server if available
            try:
                dm = DirectMessenger(self.server, self.username, self.password)
                all_messages = dm.retrieve_all()

                # Filter and display messages
                for dm_obj in all_messages:
                    if (
                        hasattr(dm_obj, 'sender')
                        and dm_obj.sender == self.recipient
                    ):
                        # This is a message FROM the selected contact
                        self.body.insert_contact_message(
                            f"{dm_obj.sender}: {dm_obj.message}"
                            )
                    elif (
                        hasattr(dm_obj, 'recipient')
                        and dm_obj.recipient == self.recipient
                    ):
                        self.body.insert_user_message(
                            f"You: {dm_obj.message}"
                            )
            except Exception as e:
                print(f"Server unavailable: {e}. Showing local messages only.")
                # If server is unavailable
                if hasattr(user_profile, 'messages') and user_profile.messages:
                    for msg in user_profile.messages:
                        if msg.get('recipient') == self.recipient:
                            # Messages sent to the current recipient
                            self.body.insert_user_message(
                                f"You: {msg.get('message')}"
                                )
                        elif msg.get('sender') == self.recipient:
                            # Messages received from the current recipient
                            self.body.insert_contact_message(
                                f"{self.recipient}: {msg.get('message')}"
                                )

        except Exception as e:
            print(f"Error displaying chat: {e}")
            import traceback
            traceback.print_exc()

    def display_all_messages(self):
        try:
            # Clear current messages
            self.body.entry_editor.delete(1.0, tk.END)

            # Get all messages
            dm = DirectMessenger(self.server, self.username, self.password)
            all_messages = dm.retrieve_all()

            # Display all messages
            for dm_obj in all_messages:
                if hasattr(dm_obj, 'sender'):
                    # Message received from someone else
                    self.body.insert_contact_message(
                        f"From {dm_obj.sender}: {dm_obj.message}"
                        )
                elif hasattr(dm_obj, 'recipient'):
                    # Message sent to someone else
                    self.body.insert_user_message(
                        f"To {dm_obj.recipient}: {dm_obj.message}"
                    )
        except Exception as e:
            print(f"Error displaying all messages: {e}")

    def check_new(self):
        try:
            # Only check for new messages if we're logged in
            if self.username and self.password and self.server:
                try:
                    dm = DirectMessenger(
                        self.server, self.username, self.password
                        )
                    new_messages = dm.retrieve_new()

                    # If there are new messages
                    if new_messages and self.recipient:
                        # Store new messages in profile for offline access
                        user_profile = Profile()
                        user_profile.load_profile(self.path)

                        # Check
                        for dm_obj in new_messages:
                            # Store the message in the profile
                            user_profile.messages.append({
                                'sender': dm_obj.sender,
                                'message': dm_obj.message,
                                'timestamp': time.time()
                            })

                            # Update the UI
                            if dm_obj.sender == self.recipient:
                                self.body.insert_contact_message(
                                    f"{dm_obj.sender}: {dm_obj.message}"
                                    )

                        # Save the updated profile
                        user_profile.save_profile(self.path)

                    self.footer.footer_label.config(text="Connected to server")
                except Exception as e:
                    print(f"Server unavailable: {e}")
                    self.footer.footer_label.config(text="Offline Mode.")
        except Exception as e:
            print(f"Error checking for new messages: {e}")

        # Schedule the next check
        self.root.after(2000, self.check_new)

    def _draw(self):
        # Build a menu and add it to the root frame.
        menu_bar = tk.Menu(self.root)
        self.root['menu'] = menu_bar
        menu_file = tk.Menu(menu_bar)

        menu_bar.add_cascade(menu=menu_file, label='File')
        menu_file.add_command(label='New Messages')
        menu_file.add_command(label='All Messages',
                              command=self.display_all_messages)
        menu_file.add_command(label='Close')

        settings_file = tk.Menu(menu_bar)
        menu_bar.add_cascade(menu=settings_file, label='Settings')
        settings_file.add_command(label='Add Contact',
                                  command=self.add_contact)
        settings_file.add_command(label='Configure DS Server',
                                  command=self.configure_server)

        # The Body and Footer classes must be initialized and
        # packed into the root window.
        self.body = Body(self.root,
                         recipient_selected_callback=self.recipient_selected)
        self.body.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        self.footer = Footer(self.root, send_callback=self.send_message)
        self.footer.pack(fill=tk.BOTH, side=tk.BOTTOM)


def main():
    # All Tkinter programs start with a root window. We will name ours 'main'.
    main = tk.Tk()

    # 'title' assigns a text value to the Title Bar area of a window.
    main.title("ICS 32 Distributed Social Messenger")

    # This is just an arbitrary starting point. You can change the value
    # around to see how the starting size of the window changes.
    main.geometry("800x600")

    # adding this option removes some legacy behavior with menus that
    # some modern OSes don't support. If you're curious, feel free to comment
    # out and see how the menu changes.
    main.option_add('*tearOff', False)

    # Initialize the MainApp class, which is the starting point for the
    # widgets used in the program. All of the classes that we use,
    # subclass Tk.Frame, since our root frame is main, we initialize
    # the class with it.
    app = MainApp(main)
    app.configure_server()

    # When update is called, we finalize the states of all widgets that
    # have been configured within the root frame. Here, update ensures that
    # we get an accurate width and height reading based on the types of widgets
    # we have used. minsize prevents the root window from resizing too small.
    # Feel free to comment it out and see how the resizing
    # behavior of the window changes.
    main.update()
    main.minsize(main.winfo_width(), main.winfo_height())
    id = main.after(2000, app.check_new)
    print(id)
    # And finally, start up the event loop for the program (you can find
    # more on this in lectures of week 9 and 10).
    main.mainloop()
