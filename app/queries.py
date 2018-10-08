import sqlite3


def connect():
    conn = sqlite3.connect("./bookshelf_database.db")
    cur = conn.cursor()
    return conn, cur

#Creation 
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------

def create_db():
    conn,cur = connect()

    cur.execute("CREATE TABLE user_info(UID integer primary key autoincrement,name varchar(50) ,street varchar(30) ,city varchar(20) ,state varchar(20) ,country varchar(20) ,contact_no int(10) ,email varchar(50),password varchar(20));")
    cur.execute("INSERT INTO user_info values(101,'Naruto','Ashokapuram','Mysuru','Karnataka','India',9016387328,'naruto@gmail.com','nar123');")
    cur.execute("INSERT INTO user_info values(null,'Sasuke','Indiranagar','Bangalore','Karnataka','India',8867352489,'sasuke@gmail.com','sas123');")

    cur.execute("CREATE TABLE lending_section(LID int ,ISBN int(10) ,book_name varchar(40) ,author varchar(50) ,av int(1) ,RID int ,foreign key(ISBN) references books(ISBN));")
    
    cur.execute("CREATE TABLE reading_section(RID int ,ISBN int(10) ,book_name varchar(40) ,author varchar(50) ,due_date date, ex_count int default 0 ,LID int ,foreign key(ISBN) references books(ISBN));")

    cur.execute("CREATE TABLE books(ISBN int(10) ,book_name varchar(40) ,author varchar(50));")
    cur.execute("INSERT INTO books values(1000000000,'Data Communications and Networking' ,'Forouzan');")
    cur.execute("INSERT INTO books values(1000000001,'System Software' ,'Leland L. Beck');")
    cur.execute("INSERT INTO books values(1000000002,'The Database Book' ,'Narain Gehani');")
    cur.execute("INSERT INTO books values(1000000003,'Modern Operating Systems' ,'Andrew S. Tanenbaum');")

    cur.execute("CREATE TABLE incomplete_transaction(RID int ,ISBN int(10) ,LID int ,foreign key(ISBN) references books(ISBN));")

    conn.commit()
    conn.close()


#Insertion
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------

def add_user(name,street,city,state,country,contact_no,email,password):
    conn,cur = connect()
    cur.execute("SELECT * FROM user_info where email = ?;",(email))
    data = cur.fetchall()
    if(data):
        return 0
    else:
        cur.execute("INSERT INTO TABLE user_info values(?,?,?,?,?,?,?,?);",[name,street,city,state,country,contact_no,email,password])
        conn.commit()
        conn.close()
        return 1        

def verify_user(email,password):
    conn,cur = connect()
    cur.execute("SELECT * FROM user_info where email = ? and password = ?;",[email,password])
    data = cur.fetchone()
    if(data):
        return 1,data
    else:
        return 0,[]

