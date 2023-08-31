import os
from flask import Flask, render_template, redirect,jsonify,request

app = Flask(__name__)


@app.route("/",methods=["GET", "POST"])
def home():
    
    name = request.form.get("name")
    code = request.form.get("room-id")
    create = request.form.get("create")
    join = request.form.get("join", False)

    if request.method == "POST":
        if not request.form.get("name"):
            error = "Name Not Provided!!"
            return render_template("home.html", name = name, code = code, error = error)
        if join != False and not request.form.get("room_id"):
            error = "Room Code Not Provided!!"
            return render_template("home.html", name = name, code = code, error = error)
        
    else:
        return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)

