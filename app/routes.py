from app import app
from flask import redirect, url_for, request, render_template
from .queries import *
app.config['SECRET_KEY'] = "YOU-WILL-NEVER-GUESS-THIS"


#To create the database for the first time
create_db()

User_Data = None
New_Book_Data = None
need_resume = False
#0:UID , 1:name , 2:street , 3: city , 4:state , 5:country , 6:contact_no , 7:email , 8:password


#Admin
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/admin_home')
def admin_home_page():
    username = request.args.get('username')
    return render_template('admin_home.html')

@app.route('/admin_books',methods = ['GET'])
def admin_get_books():
    all_books = get_all_books()
    return render_template('admin_books.html',all_books = all_books)


@app.route('/admin_get_trans',methods = ['GET'])
def admin_get_transactions():
    all_trans = get_all_transactions()
    return render_template('admin_get_trans.html',all_trans = all_trans)

@app.route('/admin_add_book',methods = ['GET'])
def admin_add_book():
    return render_template('admin_add_books.html')

@app.route('/admin_add_to_books',methods = ['POST'])
def admin_add_book_and_redirect():
    book_isbn = request.form['ISBN']
    book_name = request.form['Title']
    book_author = request.form['Author']

    admin_add_new_book(book_isbn,book_name,book_author)      
    return redirect(url_for('admin_get_books'))

#Home/Login Page
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/')
@app.route('/login')
def login():
    #get_all_tables();
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
        else:
            User_Data = list(data)
            if User_Data[0] == 100:
                return redirect(url_for('admin_home_page',username = User_Data[1]))
            else:
                return redirect(url_for('user_home_page',username = User_Data[1]))


@app.route('/user_home')
def user_home_page():
    username = request.args.get('username')
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
        if len(password)<8:
            return render_template('signup.html',msg1 = 'Password should be atleast 8 characters long')
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

def show_lends():
    global need_resume
    lent_books = get_lent_books(User_Data)
    pending_requests = get_pending_requests(User_Data)
    print(lent_books)
    return render_template('lending_section.html',name = User_Data[1],lent_books = lent_books,pending_requests = pending_requests,need_resume = need_resume)

@app.route('/lend_another_book',methods = ['GET','POST'])
def lend_another_book():
    return render_template('lend_another_book.html')

@app.route('/reject_book',methods = ['POST'])
def reject_book():
    if request.method=='POST':
        t_id = request.form['reject']
        print(type(t_id))
        accept_or_reject_the_book(t_id,0)
        return redirect(url_for('show_lends'))

@app.route('/accept_book',methods = ['POST'])
def accept_book():
    if request.method=='POST':
        t_id = request.form['accept']
        accept_or_reject_the_book(t_id,1)
        return redirect(url_for('show_lends'))

@app.route('/verify_book', methods = ['GET','POST'])
def verify_the_book():
    global New_Book_Data
    if request.method=='POST':
        isbn = request.form['isbn']
        book_name = request.form['book_name']

        if (isbn=="" or not str(isbn).isnumeric()) and book_name=="":
            return render_template('lend_another_book.html',warning_msg="Please enter book details!")
        else:
            flag,data = verify_book_details(isbn,book_name)
            if flag==True:
                for i in range(len(data)):
                    data[i] = list(data[i])
                    l = len(data)
                return render_template('lend_another_book.html',right_msg=data,len = l)
            else:
                return render_template('lend_another_book.html',warning_msg=flag)

@app.route('/add_new_lend',methods = ['POST'])
def add_lend_and_redirect():
    New_Book_Data = request.form['confirm']
    add_new_book(New_Book_Data,User_Data)
    return redirect(url_for('show_lends'))


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
    delete_removable_book(User_Data,rem_id)
    return redirect(url_for('remove_old_book'))


@app.route('/reading_section',methods = ['GET','POST'])
def read_book(return_message = "",error_message ="",available_books =""):
    all_reads = get_all_reads(User_Data)
    no_of_requests = get_no_of_requests(User_Data)
    return_message = request.args.get('return_message')
    renew_message = request.args.get('renew_message')
    prev_reads = []
    current_reads = []
    for book in all_reads:
        if book[7] == 1:
            prev_reads.append(book)
        elif book[7] == 0:
            current_reads.append(book)
    
    l = len(current_reads) + no_of_requests[0]
    return render_template('reading_section.html',username = User_Data[1],prev_reads = prev_reads,current_reads = current_reads,return_message = return_message,renew_message = renew_message,l = l )

@app.route('/return_book', methods = ['POST'])
def return_and_redirect():
    rating = request.form.get('rating',0)
    if rating != 0:    
        rating = 0.5 * int(rating)
        tran_id = request.form['return']
        rate_the_book(tran_id,rating)
    
    return_the_book(tran_id)
    return redirect(url_for('read_book',return_message = 'Returned the book successfully'))

@app.route('/renew_book',methods = ['POST'])
def renew_and_redirect():
    tran_id = request.form['renew']
    flag = renew_the_book(tran_id)
    if flag :
        return redirect(url_for('read_book',renew_message = 'Renewed the book successfully'))
    else:
        return redirect(url_for('read_book',renew_message = 'Can\'t renew the requested book'))


@app.route('/read_new_book',methods = ['POST','GET'])
def ask_for_new_book():
    error_message = request.args.get('error_message')
    available_books = request.args.getlist('available_books')
    prev_query = request.args.get('prev_query')
    prev_search_by = request.args.get('prev_search_by')
    success_message = request.args.get('success_message')
    for i in range(len(available_books)):
        available_books[i] = eval(available_books[i])   

    top_books = get_top_books()
    
    print(available_books)
    l = len(available_books)
    return render_template('read_new_book.html',success_message = success_message,error_message = error_message,available_books = available_books,prev_query = prev_query,prev_search_by = prev_search_by,top_books = top_books,len = l)

@app.route('/search_for_book',methods = ['POST'])
def search_book():
    search_by = request.form['search_by']
    if request.form['query'] != "":
        query = request.form['query']
    else:
        query = request.form['prev_search_query']    
    
    refine_by = request.form['refine_by']

    print("query = ",query)
    print(search_by)
    print(type(search_by))

    if search_by == "ISBN":
        if not query.isnumeric():
            return redirect(url_for('ask_for_new_book',error_message = "Enter valid ISBN",prev_search_by = search_by))
        else:
            available_books = search_for_books(search_by,query,refine_by,User_Data)
            if available_books == []:
                return redirect(url_for('ask_for_new_book',error_message = 'No matches found for the given ISBN and the location',available_books = available_books,prev_query = query,prev_search_by = search_by))
            else:
                return redirect(url_for('ask_for_new_book',available_books = available_books,prev_query = query,prev_search_by = search_by))
    else:
        available_books = search_for_books(search_by,query,refine_by,User_Data)
        if available_books == []:
            return redirect(url_for('ask_for_new_book',error_message = "No matches found for the given name and location",prev_query = query,prev_search_by = search_by))
        else:
            return redirect(url_for('ask_for_new_book',available_books = available_books,prev_query = query,prev_search_by = search_by))
        

@app.route('/request_book',methods = ['POST'])
def request_and_redirect():
    req_id = request.form['request_id']
    flag = request_book(req_id,User_Data)
    if flag:
        return redirect(url_for('ask_for_new_book',success_message = 'Requested successfully'))
    else:
        return redirect(url_for('ask_for_new_book',error_message = 'Oops, something went wrong!Try again!'))


@app.route('/resume_lends',methods = ['GET','POST'])
def resume_lends():
    global need_resume
    resume_lending(User_Data)
    need_resume = False
    return redirect(url_for('show_lends'))

@app.route('/pause_lends',methods = ['GET','POST'])
def pause_lends():
    global need_resume
    pause_lending(User_Data)
    need_resume = True
    return redirect(url_for('show_lends'))
                        
#User Profile Page
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/user_profile',methods = ['GET','POST'])
def display_profile():
    return render_template('user_profile.html',username = User_Data[1],email=User_Data[7],street=User_Data[2],city=User_Data[3],state=User_Data[4],country=User_Data[5],contact_number=User_Data[6],msg = None)

@app.route('/another_profile',methods = ['GET','POST'])
def display_another_profile():
    u_id = request.form['another']
    u_data = get_another_user(u_id)
    return render_template('another_user_profile.html',username = u_data[1],email=u_data[7],street=u_data[2],city=u_data[3],state=u_data[4],country=u_data[5],contact_number=u_data[6],msg = None)

@app.route('/change_password',methods = ['GET','POST'])
def get_new_password():
    return render_template('change_password.html')

@app.route('/alter_password', methods = ['POST'])
def change_password():
    global User_Data
    old_password = request.form['old_password']
    new_password = request.form['new_password']
    confirm_password = request.form['Confirm_password']

    if old_password == User_Data[8]:
        if old_password == new_password:
            return render_template('change_password.html',msg1 = 'Enter a new password')
        elif confirm_password!=new_password:
            return render_template('change_password.html',msg1 = 'Passwords don\'t match')
        else:
            update_password(User_Data,new_password)
            User_Data[8] = new_password
            return render_template('user_profile.html',username = User_Data[1],email=User_Data[7],street=User_Data[2],city=User_Data[3],state=User_Data[4],country=User_Data[5],contact_number=User_Data[6],msg = "Password updated succesfully")
    else:
        return render_template('change_password.html',msg1 = 'Wrong password')