import os

from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
import sqlite3
# from flask_mysqldb import MySQL
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, apology
from datetime import datetime 
app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
# SQL stuff
app.config['MYSQL_HOST'] = ''
app.config['MYSQL_USER'] = ''
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = ''

cwd = os.path.dirname(os.path.abspath(__file__))
path = "c:/Users/shayn/Documents/GitHub/rel-app/venv/rel_app.db"


# print("THIS IS THE CWD:", cwd)
@app.route('/', methods = ["GET", "POST"])
@login_required
def home():
    if request.method == "GET":
        connection = sqlite3.connect(path)
        db = connection.cursor()
        print("USER ID", session["user_id"])
        fName = db.execute("SELECT fName FROM users WHERE id = '{}'".format(session["user_id"])).fetchall()[0][0]
        # print(fName[0][0])
        now = datetime.now()
        hour = int(now.strftime("%H"))
        if hour < 12:
            message = "Morning"
        elif hour > 12 and hour < 6:
            message = "Afternoon"
        else:
            message = "Evening"
        return render_template("home.html", fName = fName, message = message)
    else:
        return render_template("anxiety.html")
@app.route("/stats", methods=["GET", "POST"])
def stats():
    return render_template("home.html")

@app.route("/submit", methods=["GET", "POST"])
def submit():
    return render_template("home.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user for an account."""
    # POST
    if request.method == "POST":
        # Validate form submission
        if not request.form.get("username"):
            return apology("missing username")
        elif not request.form.get("password"):
            return apology("missing password")
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords don't match")
        # Add user to database
        connection = sqlite3.connect("c:/Users/shayn/Documents/GitHub/rel-app/venv/rel_app.db")
        db = connection.cursor()
        if len(db.execute("SELECT username FROM users WHERE username = '{}'".format(request.form.get("username"))).fetchall()) > 0:
            return apology("username taken")
        db.execute("INSERT INTO users (username, hash, fName, lName) VALUES (?, ?, ?, ?)", (request.form.get("username"), generate_password_hash(request.form.get("password")), request.form.get("fName"), request.form.get("lName")))
        # db.execute("INSERT INTO users (username, hash, fName, lName) VALUES (?, ?, ?, ?)", (request.form.get("username"), generate_password_hash(request.form.get("password"))))
        connection.commit()
        id = db.execute("SELECT id FROM users WHERE username = '{}'".format(request.form.get("username"))).fetchall()[0]
        # Log user in
        session["user_id"] = id[0]

        # Let user know they're registered
        flash("Registered!")
        return redirect("/")

    # GET
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        connection = sqlite3.connect("c:/Users/shayn/Documents/GitHub/rel-app/venv/rel_app.db")
        db = connection.cursor()
        # id = db.execute("INSERT INTO users VALUES (?, ?)", (request.form.get("username"), generate_password_hash(request.form.get("password"))))
        rows = db.execute("SELECT * FROM users WHERE username = '{}'".format(request.form.get("username"))).fetchall()
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][1], request.form.get("password")):
            return apology("invalid username and/or password", 403)
        
        print('correct')
        # Remember which user has logged in
        session["user_id"] = rows[0][2]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")

