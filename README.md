# Chat-50 A chatting room website
#### Video Demo:  <URL HERE>
#### Description:

###### Libraries Uses:
- Flask
- Flask_session
- Flask_socketio
- cs50

This is my cs50 final project which is a chating app that I created using Flask library. In this project I implemented user account as well as a chat room system using data bases which was very challening and fun.

When the page is opened the user is taken to the login page if they are not already logged in. There they can register or login. Then in the home page they can either create a chat room or join one based on their needs. To join a room they can either do it via the room link or they can go into the browse room page and join a room from there.

For this program I had to learn proper **css development** to style my project in addition to that I also learned about ***Web sockets, polling and long polling***. Furthermore i also learned about **decorated functions** in this project. I also learned to use the Flask socketio library. I wanted to implement much more on this project but couldnt due to time restrictions.

# Files:
- main.py
- styles.h
- chat50.db
- ### templates
  - browse_rooms.html
  - change_password.html
  - home.html
  - layout.html
  - login.html
  - register.html
  - room.html

### main.py:
This is my main flask application file in it is the code for all the routes and the backend code.
#### Base page (layout.html):
It is the base on which the other web pages are built. It contains the responsive navigation bar which checks if user is loged in and displays options accordingly
#### register page (register.html):
Here the server checks the provided information and displays an error if anything is missing if not the users add the name, password (In a hashed form) to the database providing a user id automatically 
#### login page (login.html):
Here the server checks if the user has provided the information correctly if not an error is shown. Then the database is checked for the following name and password, which is shored in encrypted form, then it checks if the passsword is correct and logs user in with the help of sessions
#### change password (change_password.html):
Here the server checks the submited form for the password then it checks if the new password and confrmation matches if so then it changes the user's password in the database for the new one.
#### home page (home.html):
Starting with the route for home it checks weather the user selected join room button or create, For the join button it checks the rooms in chat50 database if the following room code exist if so its redirects the user to room page and changes the user's room id to that the joined. 
#### Room Rage (Room.html):
Here the *web socket* connection is established and on connection a msg is sent that the user has connected and the room members are added by one. In the **room.html** template the **createMessage** function is run for the messages sent by others and the **createUserMessage**function is run for the messages sent by the user. the file is also provided a history of pervious messages sent in the room which are then displayed similarly.
### Additional Functions:
- #### login_required:
  This is a decorated function whcih checks if the user is logged in or not. if not redirects them to login page. Used to prevent access to web pages without logging in.
- #### no_login_required: 
  This ia also a decorated fiunction which checks if user is already logged in if so redirects them to the home page used to prevent access to login and register page when user is already loged in.

- #### generate_unique_id:
  This function returns a unique 4 character long id for rooms which is not not already used by selecting 4 random characters from a list of ASCII upercase characters and checks if it is already used or not in the database.