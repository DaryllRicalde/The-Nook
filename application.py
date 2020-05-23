import os
import requests

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
Session(app)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    
    #Insert a user into a database
    name = request.form.get("user")
    password = request.form.get("password")

    return render_template("index.html")

@app.route("/login")
def login():
    
    name = request.form.get("user")
    password = request.form.get("password")

    return render_template("login.html")

@app.route("/menu", methods=["GET","POST"]) 
def menu():
        return render_template("menu.html")

@app.route("/results", methods=["POST"])
def results():
    
    query = request.form.get("query")
    search = "%" + query + "%"

    if db.execute("SELECT * FROM books WHERE isbn LIKE :search OR (title LIKE :search) OR (author LIKE :search)", {"search":search}).rowcount == 0:
        return render_template("error.html", message= "No book that matches query")
    else:
        books = db.execute("SELECT * FROM books WHERE isbn LIKE :search OR (title LIKE :search) OR (author LIKE :search)", {"search":search}).fetchall()
        return render_template("results.html", books=books)





