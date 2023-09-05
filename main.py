import os
from flask import Flask,render_template, redirect, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_socketio import join_room, leave_room, send, SocketIO
from string import ascii_uppercase
from random import choice
from cs50 import SQL
from functools import wraps

app = Flask(__name__)

app.config["SECRET_KEY"] = "hheahhvjajsjsd"

socketio = SocketIO(app)

db = SQL("sqlite:///chat50.db")
rooms = {}

def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def no_login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id"):
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function


def generate_unique_id():
    while True:
        code = ""
        # rooms = db.execute("SELECT room_id FROM rooms")
        for i in range(4):
            code += choice(ascii_uppercase)
        if code not in rooms:
            break    
    return code

@app.route("/login", methods =["GET","POST"])
@no_login_required
def login():
    if request.method == "POST":
        return "hrllo"
    else:
        return render_template("login.html")

@app.route("/register", methods =["GET","POST"])
@no_login_required
def register():
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        if not request.form.get("name"):
            error = "Please Provide Username"
            return render_template("register.html", error = error, name = name, password = password)
        elif not request.form.get("name"):
            error = "Password Not Provided"
            return render_template("register.html", error = error, name = name, password = password)
        elif not request.form.get("confirm_password"):
            error = "password confirmation not provided"
            return render_template("register.html", error = error, name = name, password = password)
        elif request.form.get("password") != request.form.get("confirm_password"):
            error = "Passwords Do Not Match"
            return render_template("register.html", error = error, name = name, password = password)
        
        rows_check = db.execute("SELECT * FROM users WHERE name = ?", name)
        if len(rows_check) != 0:
            error = "Username Already Exists"
            return render_template("register.html", error = error, name = name, password = password)

        hash = generate_password_hash(request.form.get("password"))
        db.execute("INSERT INTO users(name, hash, room_id) VALUES(?,?,?)", name, hash, None)
        
        rows = db.execute("SELECT * FROM users WHERE name = ?", name)
        session['user_id'] = rows[0]["id"]
        return redirect(url_for("home"))
    else:
        return render_template("register.html")
@app.route("/logout", methods =["GET","POST"])
@login_required
def logout():
    session.clear()

    return redirect("/")

@app.route("/profile", methods =["GET","POST"])
@login_required
def profile():
    return "TODO:"

@app.route("/",methods=["GET", "POST"])
@login_required
def home():

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
        print(session["user_id"])
        return render_template("home.html",error = "")
    
@app.route("/room")
@login_required
def room():
    return render_template("room.html", room_id = session.get("room"))

if __name__ == "__main__":
    socketio.run(app,debug=True)

