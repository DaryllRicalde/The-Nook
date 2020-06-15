from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)


class Books(db.Model):
    __tablename__ = "books"
    isbn = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    year = db.Column(db.String, nullable=False)

class Reviews(db.Model):
    __tablename__ = "reviews"
    review_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    isbn = db.Column(db.String, db.ForeignKey("books.isbn"), nullable=False)
    rating = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String, nullable=True)

    
    