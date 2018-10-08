from app import app
from flask import redirect, url_for, request, render_template
from .queries import *
app.config['SECRET_KEY'] = "YOUWILLNEVERGUESSTHIS"


#To create the database for the first time
#create_db()

User_Data = None

# @app.route('/home')
# def home():
#     return render_template('home.html')


#Home/Login Page
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')



@app.route('/verify',methods = ['POST'])
def check_credentials():
    
    global User_Data
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        flag,data = verify_user(email,password)
        if flag==0:
            return render_template('login.html',msg = "Incorrect email or password")
            #print("invalid user")
        else:
            User_Data = data
            return render_template('user_home.html',user_id = str(data[0]))

@app.route('/signup',methods = ['GET'])
def signup():
    return render_template('signup.html')

@app.route('/verify2',methods = ['POST','GET'])
def get_new_user():
    if(request.method == "POST"):
        password = request.form['password']
        c_password = request.form['Confirm_password']

        if(password!=c_password):
            return render_template('signup.html',msg1 = 'Passwords don\'t match')

        fn = request.form['Fname']
        ln = request.form['Lname']
        name = fn+' '+ln
        email = request.form['email']
        street = request.form['Street']
        city = request.form['City']
        state = request.form['State']
        country = request.form['Country']
        contact_no = request.form['Phone']

        if(len(contact_no)!=10 or not(contact_no.isnumeric())):
            return render_template('signup.html',msg2 = 'Enter valid phone number')
        else:
            add_user(name,street,city,state,country,contact_no,email,password) 
            return render_template('home.html')    
