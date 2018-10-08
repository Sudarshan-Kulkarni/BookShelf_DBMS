from app import app
from flask import redirect, url_for, request, render_template
from .queries import *
#app.config['SECRET_KEY' = "YOUWILLNEVERGUESSTHIS"]

#create_db()

User_Data = None


@app.route('/')
@app.route('/home')
def home():
    return "This is the Home Page"

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/verify',methods = ['POST'])
def get_details():
    
    global User_Data
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        flag,data = verify_user(email,password)
        if flag==0:
            return render_template('verify.html',user = "Invalid credentials, please try again.")
            #print("invalid user")
        else:
            User_Data = data
            return render_template('user_home.html')
        