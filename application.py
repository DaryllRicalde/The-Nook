import os
import requests

from flask import Flask, session, render_template, request,json,redirect,url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["GET","POST"])
def index():
    
    #Insert a user into a database
    name = request.form.get("user")
    password = request.form.get("password")
    verify = request.form.get("verify")

    if request.method == "POST":

        #Check if the username field has input
        if name == "":
            return render_template("error.html",message="Please enter a valid username")
        
        #Check if the password or verify password field has input
        if password == "":
            return render_template("error.html",message="Please enter a valid password")
        if verify == "":
            return render_template("error.html",message="Please enter a valid password")

        #Check if username already exists
        checkUser = db.execute("SELECT username FROM users WHERE username LIKE :namegiven", {"namegiven":name})
        if checkUser.rowcount > 0:
            return render_template("error.html",message="That username is already taken")
        
        #If username is valid, check if passwords are matching and if TRUE, insert the user into the database
        if password == verify:
            db.execute("INSERT INTO users (username,password) VALUES (:username, :password)", {"username":name,"password":password})
            db.commit()
            return redirect("/login")
        else:
            return render_template("error.html", message="Passwords dont match")
    if request.method == "GET":
        return render_template("index.html")

@app.route("/login", methods=["GET","POST"])
def login():
    
    #Check if user is submitting data via POST
    if request.method == "POST":

        #Check if this user exists
        name = request.form.get("user")
        password = request.form.get("password")

        user = db.execute("SELECT * FROM users WHERE username = :username AND (password =:password)", {"username":name, "password":password}).fetchone()

        #If the user does not exist or the password and username combination are wrong
        if user is None:
            return render_template("error.html", message="User does not exist, ensure that both username and password are correct.")

        else:
            user_id = user.user_id 
            return redirect(url_for("menu", user_id=user_id))

    #Check if user is wanting to access the page via GET           
    if request.method == "GET":
        return render_template("login.html")

@app.route("/menu/<user_id>", methods=["GET","POST"]) 
def menu(user_id):
    
    #Check if a valid user is trying to access the menu page via GET
    if request.method == "GET":
        if user_id is None:
            return render_template("error.html",message="Please login first")
        else:
            currUser = db.execute("SELECT * FROM users WHERE user_id =:user_id", {"user_id":user_id}).fetchone()
            name = currUser.username
            return render_template("menu.html",Username=name)

@app.route("/results", methods=["POST"])
def results():
    
    query = request.form.get("query")
    #Concat the search query with "%" before and after to use it in a SQL query
    search = "%" + query + "%"

    if db.execute("SELECT * FROM books WHERE isbn LIKE :search OR (title LIKE :search) OR (author LIKE :search)", {"search":search}).rowcount == 0:
        return render_template("error.html", message= "No book that matches query")
    else:
        books = db.execute("SELECT * FROM books WHERE isbn LIKE :search OR (title LIKE :search) OR (author LIKE :search) LIMIT 15", {"search":search}).fetchall()
        return render_template("results.html", books=books)

@app.route("/results/<isbn>", methods=["GET", "POST"])
def book(isbn):
    if request.method == "POST":
        if db.execute("SELECT * FROM books WHERE isbn =:isbn", {"isbn" :isbn}).rowcount == 0:
            return render_template("error.html", message= "No ISBN matches that query")                
    key = "VLzf2BCTUPaWOUXWddDBQ"

    #Get JSON data
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key":key, "isbns":isbn})
    query = res.json()
    data = query["books"][0]
    average = data["average_rating"]

    book = db.execute("SELECT * FROM books WHERE isbn =:isbn", {"isbn" :isbn}).fetchone()
    title = book.title
    author = book.author
    year = book.year    
    return render_template("book.html", average=average, title=title,author=author,year=year)
        






