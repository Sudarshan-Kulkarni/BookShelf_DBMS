import sqlite3


def connect():
    conn = sqlite3.connect("./bookshelf_database.db")
    cur = conn.cursor()
    return conn, cur

#Creation 
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------

def create_db():
    conn,cur = connect()
    
    # cur.execute("DROP TABLE user_info;")
    # cur.execute("DROP TABLE lending_section;") 
    # cur.execute("DROP TABLE reading_section;") 
    # cur.execute("DROP TABLE books")
    # cur.execute("DROP TABLE incomplete_transaction;")
    

    cur.execute("CREATE TABLE user_info(UID integer primary key autoincrement,name varchar(50) ,street varchar(30) ,city varchar(20) ,state varchar(20) ,country varchar(20) ,contact_no int(10) ,email varchar(50),password varchar(20));")
    cur.execute("INSERT INTO user_info values(101,'Naruto','Ashokapuram','Mysuru','Karnataka','India',9016387328,'naruto@gmail.com','nar123');")
    cur.execute("INSERT INTO user_info values(null,'Sasuke','Indiranagar','Bangalore','Karnataka','India',8867352489,'sasuke@gmail.com','sas123');")

    cur.execute("CREATE TABLE lending_section(LID integer ,ISBN int(5) ,av int(1) ,RID integer ,foreign key(ISBN) references books(ISBN));")
    cur.execute("INSERT INTO lending_section values(101 ,10000 ,1 , null);")

    """
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    Gotta take care of the book_namees and authors so as to perform joins!!!!!!!!!!!!!
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    """
    cur.execute("CREATE TABLE reading_section(RID integer ,ISBN int(5) , due_date date, extn_count int default 0 ,LID integer ,foreign key(ISBN) references books(ISBN));")

    cur.execute("CREATE TABLE books(ISBN int(5) ,book_name varchar(40) ,author varchar(50) ,popularity int DEFAULT 0);")
    cur.execute("INSERT INTO books values(10000,'Data Communications and Networking' ,'Forouzan',null);")
    cur.execute("INSERT INTO books values(10001,'System Software' ,'Leland L. Beck',null);")
    cur.execute("INSERT INTO books values(10002,'The Database Book' ,'Narain Gehani',null);")
    cur.execute("INSERT INTO books values(10003,'Modern Operating Systems' ,'Andrew S. Tanenbaum',null);")

    cur.execute("CREATE TABLE incomplete_transaction(RID integer ,ISBN int(5) ,LID integer ,foreign key(ISBN) references books(ISBN));")


    # create a trigger later for inserting a transaction into incomplete transaction table.


    conn.commit()
    conn.close()


#Insertion
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------

def add_user(name,street,city,state,country,contact_no,email,password):
    conn,cur = connect()
    cur.execute("SELECT * FROM user_info where email = ?;",(email,))
    data = cur.fetchall()
    if(data):
        conn.close()
        return 0
    else:
        cur.execute("INSERT INTO user_info values(null,?,?,?,?,?,?,?,?);",(name,street,city,state,country,contact_no,email,password,))
        conn.commit()
        conn.close()
        return 1        

def verify_book_details(isbn,bname):

    if (isbn=="" and bname!="") or (not isbn.isnumeric() and bname!=""):
        cur.execute("SELECT * FROM books where book_name=?;",(bname,))
        data = cur.fetchall()
        if(data):
            return True,data
        else:
            return "Book name is incorrect!",None
    elif isbn.isnumeric():
        cur.execute("SELECT * FROM books where ISBN=?;",(isbn,))
        data = cur.fetchall()
        conn.close()
        if(data):
            return True,data
        else:
            cur.execute("SELECT * FROM books where book_name=?;",(bname,))
            data = cur.fetchall()
            if(data):
                return True,data
            else:
                return "Enter valid details!",None


#Selection
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------

def verify_user(email,password):
    conn,cur = connect()
    cur.execute("SELECT * FROM user_info where email = ? and password = ?;",[email,password])
    data = cur.fetchone()
    if(data):
        conn.close()
        return 1,data
    else:
        conn.close()
        return 0,[]


#Updation
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------

def update_password(User_Data,new_password):
    conn,cur = connect()
    cur.execute("UPDATE user_info SET password = ? where UID = ?",(new_password,User_Data[0],))
    conn.commit()

    """changed from here
    cur.execute("SELECT * FROM user_info where UID = ? and password = ?;",[User_data[0],new_password])
    data = cur.fetchone()
    """
    conn.close()
    #return data

#Joins
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_lent_books(User_Data):
    conn,cur = connect()
    #cur.execute("SELECT L.ISBN,B.book_name,B.author,L.av,U.name,U.email,U.contact_no FROM lending_section L,books B,user_info U where L.ISBN=B.ISBN AND L.RID=U.UID AND L.LID = ?;",(User_Data[0],))
    #cur.execute("SELECT ISBN,book_name,author,av from lending_section NATURAL JOIN books INNER JOIN user_info ON lending_section.RID=user_info.UID where LID=?;",(User_Data[0],))
    cur.execute("SELECT L.ISBN,B.book_name,B.author,L.av,U.name,U.email,U.contact_no FROM lending_section L JOIN books B ON L.ISBN=B.ISBN LEFT OUTER JOIN user_info U ON L.RID=U.UID where L.LID= ?;",(User_Data[0],))
    lent_books = cur.fetchall()
    for i in range(len(lent_books)):
        lent_books[i] = list(lent_books[i])
    print(lent_books)
    for i in range(len(lent_books)):
        for j in range(len(lent_books[i])):
            if j==3:
                 if lent_books[i][j]==0:
                     lent_books[i][j] = 'Lent'
                     break
                 else:
                     lent_books[i][j] = 'Not Lent' 
                     lent_books[i][j+1] = '--'
                     lent_books[i][j+2] = '--'
                     lent_books[i][j+3] = '--'
    return lent_books