import os
from flask import Flask, render_template, redirect, request, session, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
from string import ascii_uppercase
from random import choice
from cs50 import SQL

app = Flask(__name__)

app.config["SECRET_KEY"] = "hheahhvjajsjsd"

socketio = SocketIO(app)

db = SQL("sqlite:///chat50.db")
rooms = {}

def generate_unique_id():
    while True:
        code = ""
        # rooms = db.execute("SELECT room_id FROM rooms")
        for i in range(4):
            code += choice(ascii_uppercase)
        if code not in rooms:
            break    
    return code


@app.route("/",methods=["GET", "POST"])
def home():
    session.clear()


    if request.method == "POST":
        
        # rooms = db.execute("SELECT room_id FROM rooms")
        name = request.form.get("name")
        code = request.form.get("room-id")
        create = request.form.get("create")
        join = request.form.get("join", False)
    
        if not request.form.get("name"):
            error = "Name Not Provided!!"
            return render_template("home.html", name = name, code = code, error = error)
        if join != False and request.form.get("room-id") == None:
            error = "Room Code Not Provided!!"
            return render_template("home.html", name = name, code = code, error = error)
        if join != False:
            if rooms.get(code):
                session["room"] = code
                session["name"] = name
                return redirect(url_for("room"))
            else:
                error = "Unable To Find Room"
                return render_template("home.html", name = name , code = code, error = error)
        if create != False:
            new_room_id = generate_unique_id()
            rooms[new_room_id] = {"members": 0 , "messages": []}
            session["room"] = new_room_id
            session["name"] = name
            return redirect(url_for("room"))
            #db.execute("INSERT INTO rooms (admin_id, room_id, members) VALUES (?,?,?)", 0, new_room_id, 0 )
 
            
    else:
        return render_template("home.html",error = "")
    
@app.route("/room")
def room():
    return render_template("room.html", room_id = session.get("room"))

if __name__ == "__main__":
    socketio.run(app,debug=True)

