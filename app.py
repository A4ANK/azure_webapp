import os
import redis
from flask import Flask, session, render_template, redirect, escape, request
# Configure the application name with the FLASK_APP environment variable.
app = Flask(__name__)
#app.debug = True
# Configure the secret_key with the SECRET_KEY environment variable.

app.secret_key = os.environ.get('SECRET_KEY', default=None)

# Configure the REDIS_URL constant with the REDIS_URL environment variable.
REDIS_URL = os.environ.get('REDIS_URL', default=None)


class SessionStore:
    '''
      Session Store using redis cache, with ttl = 10 seconds,
      uid == username
    '''
    def __init__(self, uid,  url=REDIS_URL, ttl=10):
        self.id = uid
        self.redis = redis.Redis.from_url(url)
        self.ttl = ttl

    def set(self, key, value):
        self.refresh()
        return self.redis.hset(self.id, key, value)

    def get(self, key):
        self.refresh()
        return self.redis.hget(self.id, key)

    def incr(self, key):
        self.refresh()
        return self.redis.hincrby(self.id, key, 1)

    def refresh(self):
        self.redis.expire(self.id, self.ttl)

@app.route('/')
def index():
    if 'username' in session:
        username = escape(session['username'])
        store = SessionStore(username, REDIS_URL)   
        visits = store.incr('visits')
        return render_template("logout.html", username=username, visits=visits)
          
    return render_template("home.html") 


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password'] = request.form['password'] 
        return redirect('/')
    return render_template("login.html")

@app.route('/logout')
def logout():
      username = escape(session['username'])
      print("User with username = \'{}\' is logged out successfully.\n User's Redis Session is also deleted".format(username)) 
      session.pop('username', None)
      return redirect('/')

@app.route('/home')
def home():
      return render_template("home.html")
@app.route('/arch')
def arch():
      return render_template("arch.html")
