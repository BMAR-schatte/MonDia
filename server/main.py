from flask import Flask, render_template, send_from_directory, request, make_response, redirect
from flask_sqlalchemy import SQLAlchemy
import hashlib
import random
from string import ascii_lowercase as abc
import json
import os
from wakeonlan import send_magic_packet
from threading import Thread
from time import sleep
from datetime import datetime


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + \
    os.path.abspath("database") + "/main.db?check_same_thread=False"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["EXCLUDED_ROUTES"] = ["login", "signup", "static", "update"]

db = SQLAlchemy(app)


def turn_on_pc(ip):
    monitor = DB.Monitor.query.filter_by(ip=ip).first()
    send_magic_packet(monitor.mac_address)


class DB:
    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String, nullable=False)
        password = db.Column(db.String, nullable=False)
        session_id = db.Column(db.String, nullable=False)
        status = db.Column(db.String, nullable=False)
        banned = db.Column(db.Boolean, nullable=False)

    class Monitor(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        pc_name = db.Column(db.String, nullable=False)
        ip = db.Column(db.String, nullable=False)
        play_time = db.Column(db.String, nullable=False)
        on = db.Column(db.Boolean, nullable=False)
        play_news = db.Column(db.Boolean, nullable=False)
        news_from = db.Column(db.String, nullable=False)
        news_to = db.Column(db.String, nullable=False)
        mac_address = db.Column(db.String, nullable=False)
        on_from = db.Column(db.String, nullable=False)
        on_to = db.Column(db.String, nullable=False)

    def hash_str(s: str) -> str:
        return hashlib.sha256(bytes(s, "utf8")).hexdigest()

    def gen_rand(l: int = 64) -> str:
        return "".join(random.choice(list(abc)+list("123456789")) for _ in range(l))


@app.before_request
def before_request():
    if "session_id" in request.cookies.keys():
        request.environ["user"] = DB.User.query.filter_by(
            session_id=request.cookies["session_id"]).first()
        if not request.environ["user"] and request.base_url.split("/")[1:][2] not in app.config["EXCLUDED_ROUTES"] and request.method != "POST":
            return redirect("/login", 302)
    else:
        url = request.base_url.split("/")[1:]
        if not url[2] in app.config["EXCLUDED_ROUTES"] and request.method != "POST":
            return redirect("/login", 302)


@app.route("/<path:path>")
def notfound_view(path):
    return render_template("404.html", title="404", user=request.environ["user"])


@app.route("/", methods=["GET", "POST"])
def dashboard_view():
    if request.method == "GET":
        monitors = DB.Monitor.query.all()
        return render_template("dashboard.html", title="Übersicht", user=request.environ["user"], monitors_connected=monitors)
    elif request.method == "POST":
        for key in request.json:
            if request.json[key] in ["", None]:
                return "Not all values are filled", 400
        pc_name = request.json["pc_name"]
        play_time = request.json["play_time"]
        if request.json["play_news"] in ["True", "true"]:
            play_news = True
        else:
            play_news = False
        if ":" in request.json["news_from"]:
            news_from = request.json["news_from"]
        else:
            return "Fehlerhafte Eingabe in News-Von", 400
        if ":" in request.json["news_to"]:
            news_to = request.json["news_to"]
        else:
            return "Fehlerhafte Eingabe in News-Bis", 400
        if ":" in request.json["hours_from"]:
            hours_from = request.json["hours_from"]
        else:
            return "Fehlerhafte Eingabe in Aktiv-on"
        if ":" in request.json["hours_from"]:
            hours_to = request.json["hours_to"]
        else:
            return "Fehlerhafte Eingabe in Aktiv-Bis"

        mon = DB.Monitor.query.filter_by(pc_name=pc_name).first()
        if mon:
            mon.play_time = play_time
            mon.play_news = bool(play_news)
            mon.news_from = news_from
            mon.news_to = news_to
            mon.on_from = hours_from
            mon.on_to = hours_to
             
        else:
            return "Failed", 400
        db.session.add(mon)
        db.session.commit()
        return "Success"


@app.route("/delete")
def delete_ep():
    mon = DB.Monitor.query.filter_by(pc_name=request.args["monitor"])
    if mon.first():
        try:
            mon.delete()
            db.session.commit()
            return "Success"
        except Exception:
            pass
    return "Error", 400


@app.route("/login", methods=["GET", "POST"])
def login_view():
    if request.method == "GET":
        return render_template("login.html", title="Login")
    if request.method == "POST":
        user = DB.User.query.filter_by(
            username=request.json["username"]).first()
        if not user:
            return "Benutzername existiert nicht",  400
        if DB.hash_str(request.json["password"]) != user.password:
            return "Falsches Passwort", 400
        resp = make_response()
        resp.set_cookie("session_id", user.session_id)
        return resp


@app.route("/signup", methods=["GET", "POST"])
def signup_view():
    if request.method == "GET":
        return render_template("signup.html", title="Signup")
    if request.method == "POST":
        if len(request.json["username"]) < 4 or len(request.json["username"]) > 19 or len(request.json["password"]) < 9 or len(request.json["password"]) > 49:
            return "Invalide Eingaben", 400
        if len(DB.User.query.filter_by(username=request.json["username"]).all()) == 0:
            cookie = DB.gen_rand()
            user = DB.User(username=request.json["username"], password=DB.hash_str(
                request.json["password"]), session_id=cookie, status="user", banned=False)
            db.session.add(user)
            db.session.commit()
            resp = make_response()
            resp.set_cookie("session_id", cookie)
            return resp
        else:
            return "Nutzer existiert bereits!", 400


@app.route("/help")
def help_view():
    return render_template("help.html", title="Hilfe", user=request.environ["user"])


@app.route("/account")
def account_view():
    return render_template("account.html", title="Account", user=request.environ["user"])


@app.route("/update", methods=["GET", "POST"])
def update_ep():
    if request.method == "GET":
        query = DB.Monitor.query.filter_by(
            pc_name=request.args["monitor"]).first()
        hour_from = int(query.on_from.split(":")[0])
        hour_to = int(query.on_to.split(":")[0])
        now = datetime.now().hour
        
        if now < hour_to and now >= hour_from and not query.on:
            turn_on_pc(query.ip)
            query.on = True
            db.session.add(query)
            db.session.commit()
        elif (now > hour_to or now < hour_from) and query.on:
            query.on = False
            db.session.add(query)
            db.session.commit()
        query = {
            "pc_name": query.pc_name,
            "ip": query.ip,
            "play_time": query.play_time,
            "on": query.on,
            "play_news": query.play_news,
            "news_from": query.news_from,
            "news_to": query.news_to
        }
        if query:
            return json.dumps(query)
        else:
            return "None", 400
    elif request.method == "POST":
        pc_name = request.json["pc_name"]
        mons = DB.Monitor.query.filter_by(pc_name=pc_name).all()
        
        if len(mons) > 0:
            if not mons[0].on:
                mons[0].on = True
                db.session.add(mons[0])
                db.session.commit()
            return json.dumps({
                "on": mons[0].on,
                "play_time": mons[0].play_time,
                "play_news": mons[0].play_news,
                "news_from": mons[0].news_from,
                "news_to": mons[0].news_to,
                "on_from": mons[0].on_from,
                "on_to": mons[0].on_to
            })
        else:
            mon = DB.Monitor(
                pc_name=request.json["pc_name"],
                ip=request.json["ip"],
                play_time="10",
                on=True,
                play_news=True,
                news_from="00:00",
                news_to="00:00",
                mac_address=request.json["mac_address"],
                on_from = 0,
                on_to = 0
            )
            db.session.add(mon)
            db.session.commit()
            return "Monitor created", 200


@app.route("/switch", methods=["POST"])
def switch_ep():
    mon = DB.Monitor.query.filter_by(ip=request.json["ip"]).first()
    if request.json["on"] and not mon.on:
        turn_on_pc(request.json["ip"])
        mon.on = True
    elif not request.json["on"] and mon.on:
        mon.on = False
    else:
        return "Failed", 400
    db.session.add(mon)
    db.session.commit()
    return "Success"


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=80, debug=True)
