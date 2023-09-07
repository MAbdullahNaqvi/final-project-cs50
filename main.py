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
        rooms = db.execute("SELECT id FROM rooms")
        for i in range(4):
            code += choice(ascii_uppercase)
        if code not in rooms:
            break    
    return code



@app.route("/login", methods =["GET","POST"])
@no_login_required
def login():
    if request.method == "POST":
        password = request.form.get("password")
        name = request.form.get("name")
        
        if not request.form.get("name"):
            error = "Name Not Provided"
            return render_template("login.html", password = password, error = error)
        
        if not request.form.get("password"):
            error = "Password Not Provided"
            return render_template("login.html", password = password, error = error)        
        
        rows = db.execute("SELECT * FROM users WHERE name = ?", name)
        if len(rows) != 1:
            return "lol"  
        if not  check_password_hash(rows[0]["hash"], password):
            error = "Invalid Name and/or Password"
            return render_template("login.html",name = name , password = password , error = error)
        
        session["user_id"] = rows[0]["id"]

        return redirect("/")
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
    if "room_id" in session:
        session.pop("room_id")
    if request.method == "POST":        
        code = request.form.get("room-id")
        create = request.form.get("create")
        join = request.form.get("join", False)
        rooms = db.execute("SELECT id FROM rooms")
            
        if join != False and request.form.get("room-id") == None:
            error = "Room Code Not Provided!!"
            return render_template("home.html",  code = code, error = error)
        
        if join != False:
            for room in rooms:
                if room["id"] == code:
                    db.execute("UPDATE users SET room_id = ? WHERE id = ?", code, session["user_id"])
                    session["room_id"] = code
                    db.execute("UPDATE users SET room_id = ? WHERE id = ?", session["room_id"], session["user_id"])
                    return redirect(url_for("room"))           
            error = "Unable To Find Room"
            return render_template("home.html",  code = code, error = error)
        
        if create != False:
            new_room_id = generate_unique_id()            
            db.execute("INSERT INTO rooms (admin_id, id, members) VALUES (?,?,?)", session["user_id"], new_room_id, 0)
            session["room_id"] = new_room_id
            db.execute("UPDATE users SET room_id = ? WHERE id = ?", session["room_id"], session["user_id"])
            return redirect(url_for("room"))
    else:
        return render_template("home.html",error = "")


@app.route("/room")
@login_required
def room():
    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    message_his = db.execute("SELECT messages.message, users.name FROM messages INNER JOIN users ON sender_id = users.id WHERE messages.room_id = ?", rows[0]["room_id"])
    if rows[0]["room_id"] == None:
        return redirect("/")
    return render_template("room.html", room_id = rows[0]["room_id"], messages = message_his, name = rows[0]["name"])


@socketio.on('connect')
def connect():
    db.execute("UPDATE users SET room_id = ? WHERE id = ?", session["room_id"], session["user_id"])
    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])    
    room_rows = db.execute("SELECT * FROM rooms WHERE id = ?", rows[0]["room_id"])
    join_room(rows[0]["room_id"])
    send({
        "name": rows[0]["name"],
        "message": " Has Joined The Room" 
        }, to=rows[0]["room_id"])
    
    db.execute("INSERT INTO messages (room_id, sender_id, message) VALUES (?,?,?)", rows[0]["room_id"],session["user_id"],"Has Joined The Room")
    db.execute("UPDATE rooms SET members = ? WHERE id = ?", room_rows[0]["members"] + 1 , rows[0]["room_id"])


@socketio.on('disconnect')
def disconnect():
    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    send({
        "name": rows[0]["name"],
        "message": " Has Left The Room" 
        }, to=rows[0]["room_id"])
    db.execute("INSERT INTO messages (room_id, sender_id, message) VALUES (?,?,?)", rows[0]["room_id"],session["user_id"],"Has Left The Room")
    room_rows = db.execute("SELECT * FROM rooms WHERE id = ?", rows[0]["room_id"])

    db.execute("UPDATE rooms SET members = ? WHERE id = ?", room_rows[0]["members"] - 1 , rows[0]["room_id"])

    room_rows = db.execute("SELECT * FROM rooms WHERE id = ?", rows[0]["room_id"])
    if room_rows[0]["members"] == 0:
        db.execute("DELETE FROM messages WHERE room_id = ?", room_rows[0]["id"])
        db.execute("UPDATE users SET room_id = NULL WHERE id = ?",session["user_id"])
        db.execute("DELETE FROM rooms WHERE id = ?",room_rows[0]["id"])
    leave_room(rows[0]["room_id"])
    db.execute("UPDATE users SET room_id = NULL WHERE id = ?",session["user_id"])

    

@socketio.on("message")
def message(data):
    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    content = {
    "name": rows[0]["name"],
    "message": data["data"]
    }
    send(content,to=rows[0]["room_id"])
    db.execute("INSERT INTO messages (room_id, sender_id, message) VALUES (?,?,?)", rows[0]["room_id"],session["user_id"],data["data"])



if __name__ == "__main__":
    socketio.run(app,debug=True, host='192.168.0.105')

