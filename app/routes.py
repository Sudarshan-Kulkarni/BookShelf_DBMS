from app import app
from flask import redirect, url_for, request, render_template




@app.route('/')
@app.route('/home')
def home():
    return "This is the Home Page"

@app.route('/login')
def login():
    return render_template('login.html')
