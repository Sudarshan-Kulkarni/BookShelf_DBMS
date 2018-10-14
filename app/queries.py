import sqlite3


def connect():
    conn = sqlite3.connect("./bookshelf_database.db")
    cur = conn.cursor()
    return conn, cur

#Creation 
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------

def create_db():
    conn,cur = connect()
    
    #cur.execute("DROP TABLE user_info;")
    #cur.execute("DROP TABLE lending_section;") 
    # cur.execute("DROP TABLE reading_section;") 
    #cur.execute("DROP TABLE books")
    # cur.execute("DROP TABLE incomplete_transaction;")
    

    cur.execute("CREATE TABLE user_info(UID integer primary key autoincrement,name varchar(50) ,street varchar(30) ,city varchar(20) ,state varchar(20) ,country varchar(20) ,contact_no int(10) ,email varchar(50),password varchar(20));")
    cur.execute("INSERT INTO user_info values(101,'Naruto','Ashokapuram','Mysuru','Karnataka','India',9016387328,'naruto@gmail.com','nar123');")
    cur.execute("INSERT INTO user_info values(null,'Sasuke','Indiranagar','Bangalore','Karnataka','India',8867352489,'sasuke@gmail.com','sas123');")

    cur.execute("CREATE TABLE lending_section(LID int ,ISBN int(10) ,av int(1) ,RID int ,foreign key(ISBN) references books(ISBN));")
    cur.execute("INSERT INTO lending_section values(101 ,1000000000 ,1 , null);")
    """
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    Gotta take care of the book_namees and authors so as to perform joins!!!!!!!!!!!!!
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    """
    cur.execute("CREATE TABLE reading_section(RID int ,ISBN int(10) , due_date date, extn_count int default 0 ,LID int ,foreign key(ISBN) references books(ISBN));")

    cur.execute("CREATE TABLE books(ISBN int(10) ,book_name varchar(40) ,author varchar(50));")
    cur.execute("INSERT INTO books values(1000000000,'Data Communications and Networking' ,'Forouzan');")
    cur.execute("INSERT INTO books values(1000000001,'System Software' ,'Leland L. Beck');")
    cur.execute("INSERT INTO books values(1000000002,'The Database Book' ,'Narain Gehani');")
    cur.execute("INSERT INTO books values(1000000003,'Modern Operating Systems' ,'Andrew S. Tanenbaum');")

    cur.execute("CREATE TABLE incomplete_transaction(RID int ,ISBN int(10) ,LID int ,foreign key(ISBN) references books(ISBN));")


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
    #eturn data

#Joins
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_lent_books(User_Data):
    conn,cur = connect()
    cur.execute("SELECT * FROM lending_section NATURAL JOIN books where LID = ? ;",(User_Data[0],))
    lent_books = cur.fetchall()
    print(lent_books)
    return lent_books