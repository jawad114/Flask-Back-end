import json, os,http
import MySQLdb
from flask_mail import Mail
from flask import Flask, render_template,request,session
import http
from werkzeug.utils import secure_filename
from flask import redirect
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import url_for
import mysql

UPLOAD_FOLDER= "E:\My_Coding\Pycharm_Project\web_develoment.py\static"
local_server=True
with open("config.json", "r") as c:
    params=json.load(c)["params"]
app=Flask(__name__)
app.secret_key="super-secret-key"
app.config["UPLOAD_FOLDER"]=UPLOAD_FOLDER

if local_server==True:
    app.config['SQLALCHEMY_DATABASE_URI']=params["local_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]
db=SQLAlchemy(app)

class contacts(db.Model):
    sno= db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    phone_num=db.Column(db.Integer, nullable=False)
    msg= db.Column(db.String(60), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)


class Posts(db.Model):
    sno= db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    slug=db.Column(db.String(20), nullable=False)
    content= db.Column(db.String(60), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    img = db.Column(db.String(60), nullable=False)


@app.route("/uploader", methods=["GET", "POST"])
def uploader():
    if "user" in session and session["user"] == params["user_email"]:
        if request.method=="POST":
            f=request.files("file")
            f.save(os.path.join(app.config["UPLOAD_FOLDER"],secure_filename(f.filename) ))
            return "UPLOADED SUCCESSFULLY"
    return


@app.route("/index.html")
def Home():
    post=Posts.query.filter_by().all()[0:2]
    return render_template("index.html", params=params, post=post)

@app.route("/about.html")
def About():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method=='POST':
        name=request.form.get('name')
        phone=request.form.get('phone')
        message=request.form.get('message')
        email=request.form.get('email')
        entry=contacts(name=name, phone_num=phone, msg=message, email=email)
        db.session.add(entry)
        db.session.commit()


    return render_template("contact.html", params=params)

@app.route("/post.html/<string:post_slug>", methods=["GET", "POST"])
def post_route(post_slug):
        post=Posts.query.filter_by(slug=post_slug).first()

        return render_template("post.html", params=params, post=post )

@app.route("/edit/<string:sno>", methods=["GET", "POST"])
def edit(sno):
    if "user" in session and session["user"] == params["user_email"]:
        if request.method=="POST":
            title=request.form.get("title")
            content=request.form.get("content")
            slug=request.form.get("slug")
            if sno=="0":
                post=Posts(title=title, content=content, slug=slug)
                db.session.add(post)
                db.session.commit
        return render_template("edit.html",params=params, sno=sno)

@app.route("/logout")
def logout():
    session.pop("user")
    return redirect("/dashboard.html")

@app.route("/delete/<string:sno>", methods=["GET", "POST"])
def delete(sno):
    if "user" in session and session["user"] == params["user_email"]:
        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect("/dashboard.html")



@app.route("/dashboard.html", methods=["GET", "POST"])
def dashboard():
    if "user" in session and session["user"]==params["user_email"]:
            post = Posts.query.all()
            return render_template("dashboard.html", params=params, post=post)

    if request.method=="POST":
        useremail=request.form.get("email")
        userpassword=request.form.get("password")
        if useremail==params["user_email"] and userpassword==params["user_password"]:
            session["user"]=useremail
            post=Posts.query.all()
            return render_template("dashboard.html", params=params, post=post)

    return render_template("login.html", params=params)

app.run(debug=True)

