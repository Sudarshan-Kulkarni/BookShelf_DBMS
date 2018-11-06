import sqlite3


def connect():
    conn = sqlite3.connect("./bookshelf_database.db")
    cur = conn.cursor()
    return conn, cur

#Creation 
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------

def create_db():
    conn,cur = connect()
    
    cur.execute("DROP TABLE IF EXISTS user_info;")
    cur.execute("DROP TABLE IF EXISTS lending_section;") 
    cur.execute("DROP TABLE IF EXISTS reading_section;") 
    cur.execute("DROP TABLE IF EXISTS books")
    cur.execute("DROP TABLE IF EXISTS incomplete_transaction;")
    cur.execute("DROP TRIGGER IF EXISTS update_due_date;")
    

    cur.execute("CREATE TABLE user_info(UID integer primary key autoincrement,name varchar(50) ,street varchar(30) ,city varchar(20) ,state varchar(20) ,country varchar(20) ,contact_no int(10) ,email varchar(50),password varchar(20));")
    cur.execute("INSERT INTO user_info values(101,'Naruto','Ashokapuram','Mysuru','Karnataka','India',9016387328,'naruto@gmail.com','nar123');")
    cur.execute("INSERT INTO user_info values(null,'Sasuke','Indiranagar','Bangalore','Karnataka','India',8867352489,'sasuke@gmail.com','sas123');")

    cur.execute("CREATE TABLE lending_section(ID integer primary key autoincrement, LID integer ,ISBN int(5) ,av int(1) ,RID integer ,lent_date date ,due_date date , transaction_id integer, foreign key(ISBN) references books(ISBN));")
    cur.execute("INSERT INTO lending_section values(100 ,101 ,10000 ,1 ,102 ,'2018-05-07' ,'2018-05-21',100);")

    cur.execute("CREATE TABLE reading_section(ID integer primary key autoincrement, RID integer ,ISBN int(5) , due_date date, extn_count int default 0 ,LID integer ,read_status integer , transaction_id integer, foreign key(ISBN) references books(ISBN));")
    cur.execute("INSERT INTO reading_section values(100 ,102 ,10000 ,'2018-05-21' ,0 ,101 ,0, 100);")
    cur.execute("CREATE TABLE books(ISBN int(5) ,book_name varchar(40) ,author varchar(50) ,popularity int DEFAULT 0);")
    cur.execute("INSERT INTO books values(10000,'Data Communications and Networking' ,'Forouzan',null);")
    cur.execute("INSERT INTO books values(10001,'System Software' ,'Leland L. Beck',null);")
    cur.execute("INSERT INTO books values(10002,'The Database Book' ,'Narain Gehani',null);")
    cur.execute("INSERT INTO books values(10003,'Modern Operating Systems' ,'Andrew S. Tanenbaum',null);")

    cur.execute("CREATE TABLE incomplete_transaction(transaction_id integer primary key autoincrement, RID integer ,ISBN int(5) ,LID integer ,foreign key(ISBN) references books(ISBN));")


    cur.execute('''CREATE TRIGGER update_due_date AFTER UPDATE OF extn_count ON reading_section
                    WHEN(NEW.extn_count = OLD.extn_count + 1)
                        BEGIN
                            UPDATE reading_section SET due_date = date(due_date,\'+7 day\');
                            UPDATE lending_section SET due_date = date(due_date,\'+7 day\');
                        END;''')
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
    conn,cur = connect()
    if (isbn=="" and bname!="") or (not isbn.isnumeric() and bname!=""):
        cur.execute("SELECT * FROM books where book_name=?;",[bname])
        data = cur.fetchone()
        conn.close()
        if(data):
            print(data)
            return True,data
        else:
            return "Book name is incorrect!",None
    elif isbn.isnumeric():
        cur.execute("SELECT * FROM books where ISBN=?;",(isbn,))
        data = cur.fetchone()
        if(data):
            print(data)
            conn.close()
            return True,data
        else:
            cur.execute("SELECT * FROM books where book_name=?;",[bname])
            data = cur.fetchone()
            if(data):
                print(data)
                conn.close()
                return True,data
            else:
                conn.close()
                return "Enter valid details!",None

def add_new_book(new_book_isbn,User_Data):
    conn,cur = connect()
    cur.execute("INSERT INTO lending_section VALUES (null,?,?,1,null,null,null,null);",(User_Data[0],new_book_isbn,))
    conn.commit()
    conn.close()
    

#Selection
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------

def verify_user(email,password):
    conn,cur = connect()
    cur.execute("SELECT * FROM user_info WHERE email = ? AND password = ?;",[email,password])
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
    cur.execute("UPDATE user_info SET password = ? WHERE UID = ?",(new_password,User_Data[0],))
    conn.commit()

    """changed from here
    cur.execute("SELECT * FROM user_info WHERE UID = ? AND password = ?;",[User_data[0],new_password])
    data = cur.fetchone()
    """
    conn.close()
    #return data

def return_the_book(tran_id):
    conn,cur = connect()
    cur.execute("UPDATE lending_section SET av = 1 WHERE transaction_id = ?",(tran_id,))
    cur.execute("UPDATE reading_section SET read_status = 1 WHERE transaction_id = ?",(tran_id,))
    conn.commit()
    conn.close()

def renew_the_book(tran_id):
    conn,cur = connect()
    cur.execute("SELECT extn_count FROM reading_section WHERE transaction_id = ?",(tran_id,))
    extn_count = int(cur.fetchone()[0])
    print(extn_count)
    if extn_count < 3:
        cur.execute("UPDATE reading_section SET extn_count = extn_count+1 WHERE transaction_id = ?",(tran_id,))
        conn.commit()
        flag = True
    else:
        flag = False
    conn.close()
    return flag
#Joins
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_lent_books(User_Data):
    conn,cur = connect()
    #cur.execute("SELECT L.ISBN,B.book_name,B.author,L.av,U.name,U.email,U.contact_no FROM lending_section L,books B,user_info U where L.ISBN=B.ISBN AND L.RID=U.UID AND L.LID = ?;",(User_Data[0],))
    #cur.execute("SELECT ISBN,book_name,author,av from lending_section NATURAL JOIN books INNER JOIN user_info ON lending_section.RID=user_info.UID where LID=?;",(User_Data[0],))
    cur.execute("SELECT L.ID,L.ISBN,B.book_name,B.author,L.av,U.name,U.email,U.contact_no FROM lending_section L JOIN books B ON L.ISBN=B.ISBN LEFT OUTER JOIN user_info U ON L.RID=U.UID where L.LID= ?;",(User_Data[0],))
    lent_books = cur.fetchall()
    for i in range(len(lent_books)):
        lent_books[i] = list(lent_books[i])
    
    print(lent_books)
    for i in range(len(lent_books)):
        if lent_books[i][4]==0:
            lent_books[i][4] = 'Lent'
            break
        else:
            lent_books[i][4] = 'Not Lent'
            lent_books[i][4+1] = '--'
            lent_books[i][4+2] = '--'
            lent_books[i][4+3] = '--'

    conn.close()
    return lent_books

"""
ATTENTION----------------------------
UPDATE THE ABOVE FUNCTION AFTER COMPLETING READING SECTION TO INCLUDE READER'S DATA IF THE BOOK HAS BEEN LENT
-------------------------------------
"""

def get_removable_books(User_Data):
    conn,cur = connect()
    cur.execute("SELECT ID,ISBN,book_name,author FROM lending_section NATURAL JOIN books WHERE LID= ? AND av=1;",(User_Data[0],))
    data = cur.fetchall()
    conn.close()
    for i in range(len(data)):
        data[i] = list(data[i])
    return data

def delete_removable_book(User_Data,rem_id):
    conn,cur = connect()
    cur.execute("DELETE FROM lending_section WHERE LID = ? AND ID = ?;",(User_Data[0],rem_id))
    conn.commit()
    conn.close()

def get_all_reads(User_Data):
    conn,cur = connect()
    cur.execute("SELECT R.ID,R.ISBN,B.book_name,B.author,U.name,U.email,U.contact_no,R.due_date,R.extn_count,R.read_status,R.transaction_id FROM reading_section R JOIN books B ON R.ISBN = B.ISBN JOIN user_info U ON R.LID = U.UID WHERE R.RID = ?",(User_Data[0],))
    all_reads = cur.fetchall()
    conn.close()
    return all_reads