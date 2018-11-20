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
    cur.execute("DROP TRIGGER IF EXISTS set_requests_status;")
    cur.execute("DROP VIEW IF EXISTS rem_books;")
    

    cur.execute("CREATE TABLE user_info(UID integer primary key autoincrement,name varchar(50) ,street varchar(30) ,city varchar(20) ,state varchar(20) ,country varchar(20) ,contact_no int(10) ,email varchar(50),password varchar(20));")
    cur.execute("INSERT INTO user_info values(101,'Naruto','Ashokapuram','Mysuru','Karnataka','India',9016387328,'naruto@gmail.com','nar123');")
    cur.execute("INSERT INTO user_info values(null,'Sasuke','Indiranagar','Bangalore','Karnataka','India',8867352489,'sasuke@gmail.com','sas123');")

    cur.execute("CREATE TABLE lending_section(ID integer primary key autoincrement, LID integer ,ISBN int(5) ,av int(1) ,RID integer ,lent_date date ,due_date date , transaction_id integer, foreign key(ISBN) references books(ISBN));")
    cur.execute("INSERT INTO lending_section values(null ,101 ,10000 ,1 ,102 ,'2018-05-07' ,'2018-05-21',100);")

    cur.execute("CREATE TABLE reading_section(ID integer primary key autoincrement, RID integer ,ISBN int(5) , due_date date, extn_count int default 0 ,LID integer ,read_status integer , transaction_id integer, foreign key(ISBN) references books(ISBN));")
    cur.execute("CREATE TABLE books(ISBN int(5) ,book_name varchar(40) ,author varchar(50) ,popularity int DEFAULT 0);")
    cur.execute("INSERT INTO books values(10000,'Data Communications and Networking' ,'Forouzan',null);")
    cur.execute("INSERT INTO books values(10001,'System Software' ,'Leland L. Beck',null);")
    cur.execute("INSERT INTO books values(10002,'The Database Book' ,'Narain Gehani',null);")
    cur.execute("INSERT INTO books values(10003,'Modern Operating Systems' ,'Andrew S. Tanenbaum',null);")

    cur.execute("CREATE TABLE incomplete_transaction(transaction_id integer primary key autoincrement,RID integer ,LID integer ,L_ID integer ,t_date date);")
    cur.execute('INSERT INTO incomplete_transaction VALUES(100,null,null,null,null)')

    cur.execute('''CREATE TRIGGER set_request_status AFTER INSERT ON incomplete_transaction
                    BEGIN
                        UPDATE lending_section SET av = 2 WHERE ID IN (SELECT L_ID FROM incomplete_transaction);
                    END;
                ''')

    cur.execute('''CREATE TRIGGER update_due_date AFTER UPDATE OF extn_count ON reading_section
                    WHEN(NEW.extn_count > OLD.extn_count)
                        BEGIN 
                            UPDATE reading_section SET due_date = date(due_date,\'+7 day\') WHERE transaction_id = NEW.transaction_id;
                            UPDATE lending_section SET due_date = date(due_date,\'+7 day\') WHERE transaction_id = NEW.transaction_id;
                        END;
                ''')

    cur.execute('''CREATE VIEW rem_books AS
                    SELECT ID,ISBN,book_name,author,LID FROM lending_section NATURAL JOIN books WHERE (av = 1 OR av = 3);
                ''')


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

def verify_book_details(isbn,query):
    conn,cur = connect()
    if (isbn=="" and query!="") or (not isbn.isnumeric() and query!=""):
        cur.execute("SELECT * FROM books WHERE book_name LIKE '%"+query+"%';")
        data = cur.fetchall()
        conn.close()
        if(data):
            print(data)
            return True,data
        else:
            return "Book name is incorrect!",None
    elif isbn.isnumeric():
        cur.execute("SELECT * FROM books where ISBN=?;",(isbn,))
        data = cur.fetchall()
        if(data):
            print(data)
            conn.close()
            return True,data
        else:
            cur.execute("SELECT * FROM books where book_name LIKE '%"+query+"%';")
            data = cur.fetchall()
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
    

def request_book(req_id,User_Data):
    conn,cur = connect()
    cur.execute("SELECT L_ID FROM incomplete_transaction WHERE L_ID = ?",(req_id,))
    data = cur.fetchall()
    if(data):
        conn.close()
        return False

    cur.execute("INSERT INTO incomplete_transaction SELECT null,?,LID,?,date('now') FROM lending_section WHERE ID = ?;",(User_Data[0],req_id,req_id,))
    cur.execute("SELECT * FROM incomplete_transaction;")
    incomplete_transactions = cur.fetchall() 
    print("incomplete transactions = ",incomplete_transactions)
    conn.commit()
    conn.close()
    return True

    

#Selection and Deletion
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


def accept_or_reject_the_book(tran_id,flag):
    conn,cur = connect()
    cur.execute("SELECT L_ID,RID FROM incomplete_transaction WHERE transaction_id = ?;",(tran_id,))
    t = cur.fetchone()
    print(t)
    L_ID = t[0]
    RID = t[1]
    if flag == 1:
        cur.execute("SELECT ISBN FROM lending_section WHERE ID = ?",(L_ID,))
        temp = cur.fetchone()
        new_ISBN = temp[0]
        cur.execute("UPDATE lending_section SET av = 0 WHERE ID = ?",(L_ID,))
        cur.execute("UPDATE lending_section SET RID = ? WHERE ID = ?",(RID,L_ID,))
        cur.execute("UPDATE lending_section SET transaction_id = ? WHERE ID = ?",(tran_id,L_ID,))
        cur.execute("UPDATE lending_section SET lent_date = date('now','+31 day') WHERE ID = ?",(L_ID,))
        cur.execute("INSERT INTO reading_section SELECT NULL,RID,?,date('now','+31 day'),0,LID,0,transaction_id FROM incomplete_transaction WHERE transaction_id = ?;",(new_ISBN,tran_id,))
    else:
        cur.execute("UPDATE lending_section SET av = 1 WHERE ID = ?",(L_ID,))

    cur.execute("DELETE FROM incomplete_transaction where transaction_id = ?;",(tran_id,))
    conn.commit()
    conn.close()

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

def resume_lending(User_Data):
    conn,cur = connect()
    cur.execute("UPDATE lending_section SET av = 1 WHERE av = 3 AND LID = ?;",(User_Data[0],))
    conn.commit()
    conn.close()

def pause_lending(User_Data):
    conn,cur = connect()
    cur.execute("DELETE FROM incomplete_transaction WHERE transaction_id IN (SELECT transaction_id FROM lending_section WHERE av = 2 AND LID = ?);",(User_Data[0],))
    cur.execute("UPDATE lending_section SET av = 3 WHERE (av = 2 OR av = 1) AND LID = ?;",(User_Data[0],))
    conn.commit()
    conn.close()

#Joins
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------

def get_lent_books(User_Data):
    conn,cur = connect()
    cur.execute("SELECT L.ID,L.ISBN,B.book_name,B.author,L.av,L.lent_date,U.name,U.UID FROM lending_section L JOIN books B ON L.ISBN=B.ISBN LEFT OUTER JOIN user_info U ON L.RID=U.UID WHERE L.LID= ? ORDER BY L.ISBN;",(User_Data[0],))
    lent_books = cur.fetchall()
    for i in range(len(lent_books)):
        lent_books[i] = list(lent_books[i])
    
    for i in range(len(lent_books)):
        if lent_books[i][4]==0:
            lent_books[i][4] = 'Lent'
        elif lent_books[i][4]==2:
            lent_books[i][4] = 'Requested'
            lent_books[i][4+1] = '--'
            lent_books[i][4+2] = '--'
            lent_books[i][4+3] = '--'
        elif lent_books[i][4]==3:
            lent_books[i][4] = 'Paused'
            lent_books[i][4+1] = '--'
            lent_books[i][4+2] = '--'
            lent_books[i][4+3] = '--'
        else:
            lent_books[i][4] = 'Not Lent'
            lent_books[i][4+1] = '--'
            lent_books[i][4+2] = '--'
            lent_books[i][4+3] = '--'

    conn.close()
    return lent_books

def get_pending_requests(User_Data):
    conn,cur = connect()
    cur.execute("SELECT L.ISBN,B.book_name,B.author,U.name,L.ID,I.transaction_id,L.LID,U.UID FROM lending_section L JOIN incomplete_transaction I ON L.LID = I.LID JOIN books B ON L.ISBN = B.ISBN JOIN user_info U ON I.RID = U.UID WHERE L.LID = ? AND L.av = 2 AND L.ID = I.L_ID",(User_Data[0],))
    pending_requests = cur.fetchall()
    print("pending requests = ",pending_requests)
    conn.close()
    return pending_requests

def get_removable_books(User_Data):
    conn,cur = connect()
    # cur.execute("SELECT ID,ISBN,book_name,author FROM lending_section NATURAL JOIN books WHERE LID= ? AND av=1;",(User_Data[0],))
    cur.execute("SELECT * FROM rem_books WHERE LID = ?;",(User_Data[0],))
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
    cur.execute("SELECT R.ID,R.ISBN,B.book_name,B.author,U.name,R.due_date,R.extn_count,R.read_status,R.transaction_id,U.UID FROM reading_section R JOIN books B ON R.ISBN = B.ISBN JOIN user_info U ON R.LID = U.UID WHERE R.RID = ?",(User_Data[0],))
    all_reads = cur.fetchall()
    print(all_reads)
    conn.close()
    return all_reads

def search_for_books(search_by,query,refine_by,User_Data):
    conn,cur = connect()
    if search_by == 'ISBN':
        if refine_by == 'street':
            cur.execute("SELECT L.LID,L.ID,L.ISBN,B.book_name,B.author,U.name,U.street,U.city,U.state,U.country,U.UID FROM lending_section L JOIN books B ON L.ISBN=B.ISBN JOIN user_info U ON U.UID = L.LID WHERE L.ISBN = ? AND U.street = ? AND L.av = 1 AND LID != ?;",(query,User_Data[2],User_Data[0],))
        elif refine_by == 'city':
            cur.execute("SELECT L.LID,L.ID,L.ISBN,B.book_name,B.author,U.name,U.street,U.city,U.state,U.country,U.UID FROM lending_section L JOIN books B ON L.ISBN=B.ISBN JOIN user_info U ON U.UID = L.LID WHERE L.ISBN = ? AND U.city = ? AND L.av = 1 AND LID != ?;",(query,User_Data[3],User_Data[0],))
        elif refine_by == 'state':
            cur.execute("SELECT L.LID,L.ID,L.ISBN,B.book_name,B.author,U.name,U.street,U.city,U.state,U.country,U.UID FROM lending_section L JOIN books B ON L.ISBN=B.ISBN JOIN user_info U ON U.UID = L.LID WHERE L.ISBN = ? AND U.state = ? AND L.av = 1 AND LID != ?;",(query,User_Data[4],User_Data[0],))
        
    else:
        if refine_by == 'street':
            cur.execute("SELECT L.LID,L.ID,L.ISBN,B.book_name,B.author,U.name,U.street,U.city,U.state,U.country,U.UID FROM lending_section L JOIN books B ON L.ISBN=B.ISBN JOIN user_info U ON U.UID = L.LID WHERE B.book_name LIKE '%"+query+"%' AND U.street = ? AND L.av = 1 AND LID != ?;",(User_Data[2],User_Data[0],))
        elif refine_by == 'city':
            cur.execute("SELECT L.LID,L.ID,L.ISBN,B.book_name,B.author,U.name,U.street,U.city,U.state,U.country,U.UID FROM lending_section L JOIN books B ON L.ISBN=B.ISBN JOIN user_info U ON U.UID = L.LID WHERE B.book_name LIKE '%"+query+"%' AND U.city = ? AND L.av = 1 AND LID != ?;",(User_Data[3],User_Data[0],))
        elif refine_by == 'state':
            cur.execute("SELECT L.LID,L.ID,L.ISBN,B.book_name,B.author,U.name,U.street,U.city,U.state,U.country,U.UID FROM lending_section L JOIN books B ON L.ISBN=B.ISBN JOIN user_info U ON U.UID = L.LID WHERE B.book_name LIKE '%"+query+"%' AND U.state = ? AND L.av = 1 AND LID != ?;",(User_Data[4],User_Data[0],))

    available_books = cur.fetchall()
    conn.close()    
    return available_books


def get_another_user(u_id):
    conn,cur = connect()
    cur.execute("SELECT * FROM user_info WHERE UID = ?;",(u_id,))
    data = cur.fetchone()
    conn.close()
    return data

def get_no_of_requests(User_Data):
    conn,cur = connect()
    cur.execute("SELECT COUNT(*) FROM incomplete_transaction WHERE RID = ?;",(User_Data[0],))
    data = cur.fetchone()
    conn.close()
    if data:
        return data
    else:
        return 0