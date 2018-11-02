from app import app
from flask import redirect, url_for, request, render_template
from .queries import *
app.config['SECRET_KEY'] = "YOU-WILL-NEVER-GUESS-THIS"


#To create the database for the first time
#create_db()

User_Data = None
New_Book_Data = None
#0:UID , 1:name , 2:street , 3: city , 4:state , 5:country , 6:contact_no , 7:email , 8:password

# @app.route('/home')
# def home():
#     return render_template('home.html')


#Home/Login Page
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')



@app.route('/verifyLogin',methods = ['POST'])
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
            User_Data = list(data)
            return render_template('user_home.html',username = User_Data[1])

@app.route('/user_home')
def user_home_page():
    return render_template('user_home.html',username = User_Data[1])


#Signup Page
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/signup',methods = ['GET'])
def signup():
    return render_template('signup.html')

@app.route('/verifySignUp',methods = ['POST','GET'])
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
            flag = add_user(name,street,city,state,country,contact_no,email,password)

            if flag==0:
                return render_template('signup.html',msg2 = 'Email is already registered')
            elif flag==1: 
                return render_template('login.html',msg1 = "Registration Successful!")    

#Lending and Reading Section Pages
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/lending_section',methods = ['GET','POST'])
def add_book():
    global New_Book_Data

    if request.method =='POST':
        New_Book_Data = request.form['confirm']
        print(New_Book_Data)
        add_new_book(New_Book_Data,User_Data)
        New_Book_Data = None

    return lend_book()

def lend_book():
    lent_books = get_lent_books(User_Data)
    return render_template('lending_section.html',name = User_Data[1],lent_books = lent_books)

@app.route('/lend_another_book',methods = ['GET','POST'])
def lend_another_book():
    return render_template('lend_another_book.html')

@app.route('/verify_book', methods = ['GET','POST'])
def verify_the_book():
    global New_Book_Data
    if request.method=='POST':
        isbn = request.form['isbn']
        book_name = request.form['book_name']
        print(type(isbn))

        if (isbn=="" or not str(isbn).isnumeric()) and book_name=="":
            return render_template('lend_another_book.html',warning_msg="Please enter book details!")
        else:
            flag,data = verify_book_details(isbn,book_name)
            print(flag)
            if flag==True:
                print("HI-BYE")
                #for i in range(len(data)):
                #      data[i] = list(data[i])
                #    del data[i][3]
                data = list(data)
                del data[3]
                #New_Book_Data = data
                print(data)
                return render_template('lend_another_book.html',right_msg=data,book = data[0])
            else:
                return render_template('lend_another_book.html',warning_msg=flag)



@app.route('/remove_lent_book', methods = ['POST','GET'])

def remove_old_book():
    if request.method=='POST':
        print(request.form)
    return ask_which_book()
def ask_which_book():
    removable_books = get_removable_books(User_Data)
    return render_template('remove_lent_book.html',removable_books = removable_books)

@app.route('/remove_the_lent_book', methods = ['POST'])
def remove_and_redirect():
    rem_id = request.form['remove']
    print("rem_id = ",rem_id)
    delete_removable_book(User_Data,rem_id)
    return redirect(url_for('remove_old_book'))

@app.route('/reading_section',methods = ['GET','POST'])
def read_book():
    return render_template('reading_section.html',op1 = 'naruto',op2 = 'sasuke',username = User_Data[1])

#User Profile Page
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/user_profile',methods = ['GET','POST'])
def display_profile():
    return render_template('user_profile.html',username = User_Data[1],email=User_Data[7],street=User_Data[2],city=User_Data[3],state=User_Data[4],country=User_Data[5],contact_number=User_Data[6],msg = None)

@app.route('/change_password',methods = ['GET','POST'])
def get_new_password():
    return render_template('change_password.html')

@app.route('/alter_password', methods = ['POST'])
def change_password():
    global User_Data
    old_password = request.form['old_password']
    new_password = request.form['new_password']
    confirm_password = request.form['Confirm_password']

    #checking if the old password entered is right
    if old_password == User_Data[8]:
        if old_password == new_password:
            return render_template('change_password.html',msg1 = 'Enter a new password')
        elif confirm_password!=new_password:
            return render_template('change_password.html',msg1 = 'Passwords don\'t match')
        else:
            update_password(User_Data,new_password)
            User_Data[8] = new_password
            return render_template('user_profile.html',username = User_Data[1],email=User_Data[7],street=User_Data[2],city=User_Data[3],state=User_Data[4],country=User_Data[5],contact_number=User_Data[6],msg = "Password updated succesfully")
            #return render_template('user_home.html',username = User_Data[1])
    else:
        return render_template('change_password.html',msg1 = 'Wrong password')


# @app.route('/action', methods = ['POST'])
# def test():
#     message = request.form['subject'] 
#     return render_template('reading_section.html',op1 = 'naruto',op2 = 'sasuke',msg = message)
