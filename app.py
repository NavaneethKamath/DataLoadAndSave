
import email
import json
from urllib import request
from flask import *
from flask_bootstrap import *

from flask_mongoengine import MongoEngine


import requests


app = Flask(__name__)
DB_URI = "mongodb+srv://Navaneeth:Jnnce123@cluster0.1g6b9.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
app.config["MONGODB_HOST"] = DB_URI
db = MongoEngine()
db.init_app(app)


class User(db.Document):
    name = db.StringField()
    email = db.StringField()
    password = db.StringField()

    def to_json(self):
        return {
            "name": self.name,
            "email": self.email,
            "password": self.password
        }
    
class MSG(db.Document):
    key = db.StringField()
    msg = db.StringField()
    

    def to_json(self):
        return {
            "key": self.key,
            "msg": self.msg
            
        }
    

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        if(request.form['password'] == request.form['agpassword']):
            data = {
                "name": request.form['name'],
                "email": request.form['email'],
                "password": request.form['password']}
            data = json.dumps(data)
            record = json.loads(data)
            d = User(name=record['name'], email=record['email'],password=record['password'])
            m=User.objects(email=request.form['email'])
            if m:
                return render_template("register.html", error="ERROR : USER EXISTS.")
            else:
                d.save()

                return render_template("register.html", done="SUCCESS : ACCOUNT CREATED.")
            #response= requests.post(url="http://127.0.0.1:5000/",data=data)

        else:
            return render_template("register.html", error="ERROR : PASSWORD MISMATCH.")



@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form['email']
        password = request.form['password']
        
        u = User.objects(email=username)
        
        if not u:
            return render_template("login.html",error="ERROR : USER ACCOUNT DOESN'T EXIST.")
        else:
            m=json.dumps(u)
            m=m[1:len(m)-1]
            s=json.loads(m)
            if(password == s['password']):
                resp = make_response(redirect('/home'))
                name = s['name']
                email = s['email']
                resp.set_cookie('user', name)
                resp.set_cookie('email', email)
                return resp
            else:
                return render_template("login.html", error="ERROR : WRONG PASSWORD.")


@app.route('/home', methods=['GET', 'POST'])
def home():
    if (request.cookies.get('user')):
        user = request.cookies.get('user')
        msgs=MSG.objects()
        
        return render_template("home.html", user=user,msg=msgs)

    else:
        return render_template("login.html", error="UNAUTHORIZED LOGIN.")

@app.route('/add', methods=['GET', 'POST'])
def add():
    if (request.cookies.get('user')):
        if request.method=="GET":
            return render_template('add.html')
        else:
            data = {
                "key": request.form['key'],
                "msg": request.form['msg']
                }
            data = json.dumps(data)
            record = json.loads(data)
            d = MSG(key=record['key'],msg=record['msg'])
            d.save()
            user=request.cookies.get('user')
            resp = make_response(redirect('/home'))
            return resp


    else:
        return render_template("login.html", error="UNAUTHORIZED LOGIN.")

@app.route('/logout')
def logout():
    resp = make_response(render_template('login.html', data="Successful Logout."))
    resp.set_cookie('user', '', expires=0)
    resp.set_cookie('email','',expires=0)
    return resp
if __name__ == "__main__":
    app.run(debug=True)
