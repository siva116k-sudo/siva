"""
COMPLETE INDIA RAILWAY DATABASE — 141 Trains
Covers: Metro cities, Towns, Villages across all states
Run: python seed_data.py
"""

import sqlite3
from datetime import datetime
import hashlib

DATABASE = 'database.db'

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def seed():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row

    db.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            reset_token TEXT,
            token_expiry TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS trains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            train_no TEXT UNIQUE NOT NULL,
            train_name TEXT NOT NULL,
            from_station TEXT NOT NULL,
            to_station TEXT NOT NULL,
            departure TEXT NOT NULL,
            arrival TEXT NOT NULL,
            total_seats INTEGER NOT NULL,
            available_seats INTEGER NOT NULL,
            price_per_seat REAL NOT NULL,
            train_type TEXT DEFAULT "Express",
            image TEXT DEFAULT "rajdhani.jpg"
        );
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pnr TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            train_id INTEGER NOT NULL,
            seats TEXT NOT NULL,
            journey_date TEXT NOT NULL,
            total_price REAL NOT NULL,
            status TEXT DEFAULT "confirmed",
            transaction_id TEXT,
            booked_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (train_id) REFERENCES trains(id)
        );
    ''')

    db.execute('DELETE FROM trains')
    db.execute('DELETE FROM users')
    print("Cleared old data")

    users = [
        ('admin','admin@railbook.com',hash_pw('admin123'),1),
        ('rahul','rahul@gmail.com',hash_pw('rahul123'),0),
        ('priya','priya@gmail.com',hash_pw('priya123'),0),
        ('arun','arun@gmail.com',hash_pw('arun123'),0),
        ('sneha','sneha@gmail.com',hash_pw('sneha123'),0),
        ('vikram','vikram@gmail.com',hash_pw('vikram123'),0),
    ]
    for u in users:
        try:
            db.execute('INSERT INTO users (username,email,password,is_admin) VALUES (?,?,?,?)',u)
        except: pass

    trains = [
        # RAJDHANI
        ('12301','Howrah Rajdhani Express','HWH','NDLS','14:05','10:05',72,72,2100.0,'Rajdhani','rajdhani.jpg'),
        ('12302','New Delhi Rajdhani Express','NDLS','HWH','16:55','12:55',72,72,2100.0,'Rajdhani','rajdhani.jpg'),
        ('12433','Chennai Rajdhani Express','NDLS','MAS','15:00','15:45',68,68,2400.0,'Rajdhani','rajdhani.jpg'),
        ('12431','Thiruvananthapuram Rajdhani','NDLS','TVC','11:00','11:25',68,68,2500.0,'Rajdhani','rajdhani.jpg'),
        ('12423','Dibrugarh Rajdhani Express','NDLS','DBG','21:35','04:40',68,68,2200.0,'Rajdhani','rajdhani.jpg'),
        ('12453','Ranchi Rajdhani Express','NDLS','RNC','20:00','14:00',68,68,1950.0,'Rajdhani','rajdhani.jpg'),
        ('12305','Howrah Mumbai Rajdhani','HWH','CSTM','13:35','21:30',72,72,2300.0,'Rajdhani','rajdhani.jpg'),
        ('22691','Bangalore Rajdhani Express','NDLS','SBC','20:00','06:00',68,68,2350.0,'Rajdhani','rajdhani.jpg'),
        # SHATABDI
        ('12001','Bhopal Shatabdi Express','NDLS','BPL','06:00','13:55',60,60,1200.0,'Shatabdi','shatabdi.jpg'),
        ('12009','Mumbai Pune Shatabdi','MMCT','PUNE','06:25','10:05',56,56,950.0,'Shatabdi','shatabdi.jpg'),
        ('12027','Chennai Vijayawada Shatabdi','MAS','BZA','06:00','13:45',60,60,1100.0,'Shatabdi','shatabdi.jpg'),
        ('12031','Amritsar Shatabdi Express','NDLS','ASR','16:40','22:40',64,64,900.0,'Shatabdi','shatabdi.jpg'),
        ('12045','Chandigarh Shatabdi Express','NDLS','CDG','07:40','11:20',60,60,750.0,'Shatabdi','shatabdi.jpg'),
        ('12047','Ajmer Shatabdi Express','NDLS','AII','06:05','12:40',60,60,850.0,'Shatabdi','shatabdi.jpg'),
        ('12019','Bhubaneswar Shatabdi','HWH','BBS','06:25','14:20',60,60,1050.0,'Shatabdi','shatabdi.jpg'),
        # VANDE BHARAT
        ('22435','New Delhi Varanasi Vande Bharat','NDLS','BSB','06:00','14:00',50,50,1800.0,'Vande Bharat','vande_bharat.jpg'),
        ('20901','Mumbai Ahmedabad Vande Bharat','MMCT','ADI','06:10','12:30',50,50,1500.0,'Vande Bharat','vande_bharat.jpg'),
        ('20907','Chennai Bangalore Vande Bharat','MAS','SBC','06:00','11:00',50,50,1400.0,'Vande Bharat','vande_bharat.jpg'),
        ('22549','Secunderabad Vizag Vande Bharat','SC','VSKP','05:45','12:30',50,50,1350.0,'Vande Bharat','vande_bharat.jpg'),
        ('22901','Mumbai Gandhinagar Vande Bharat','MMCT','GNA','06:25','10:45',50,50,1200.0,'Vande Bharat','vande_bharat.jpg'),
        ('22415','Ajmer New Delhi Vande Bharat','AII','NDLS','05:45','11:55',50,50,1300.0,'Vande Bharat','vande_bharat.jpg'),
        ('20951','Mumbai Goa Vande Bharat','MMCT','MAO','05:25','13:55',50,50,1600.0,'Vande Bharat','vande_bharat.jpg'),
        # DURONTO
        ('12213','Mumbai LTT Duronto Express','LTT','NDLS','23:25','22:45',80,80,1700.0,'Duronto','duronto.jpg'),
        ('12285','Secunderabad Duronto Express','SC','NDLS','06:20','10:30',80,80,1900.0,'Duronto','duronto.jpg'),
        ('22209','Mumbai New Delhi Duronto','MMCT','NDLS','23:00','19:45',80,80,1800.0,'Duronto','duronto.jpg'),
        ('12269','Chennai Duronto Express','MAS','NDLS','09:25','13:50',80,80,2000.0,'Duronto','duronto.jpg'),
        # TEJAS
        ('82501','Mumbai Ahmedabad Tejas Express','MMCT','ADI','06:40','13:10',56,56,1850.0,'Tejas','vande_bharat.jpg'),
        ('82901','Delhi Lucknow Tejas Express','NDLS','LKO','06:10','12:25',56,56,1600.0,'Tejas','vande_bharat.jpg'),
        ('82902','Lucknow Delhi Tejas Express','LKO','NDLS','14:35','21:35',56,56,1600.0,'Tejas','vande_bharat.jpg'),
        # SUPERFAST
        ('12951','Mumbai Rajdhani Superfast','MMCT','NDLS','17:00','08:35',90,90,1650.0,'Superfast','rajdhani.jpg'),
        ('12621','Tamil Nadu SF Express','NDLS','MAS','22:30','07:40',90,90,1450.0,'Superfast','shatabdi.jpg'),
        ('12839','Howrah Mail Express','HWH','MAS','23:55','05:25',84,84,1350.0,'Mail','duronto.jpg'),
        ('12615','Grand Trunk Express','NDLS','MAS','18:30','06:50',84,84,1300.0,'Express','duronto.jpg'),
        ('12627','Karnataka Express','NDLS','SBC','22:30','09:45',90,90,1400.0,'Express','rajdhani.jpg'),
        ('12721','Dakshin Express','NDLS','HYB','22:30','18:00',84,84,1250.0,'Express','duronto.jpg'),
        ('11057','Amritsar Mumbai Express','ASR','CSTM','17:40','04:30',84,84,1100.0,'Express','shatabdi.jpg'),
        ('12903','Golden Temple Mail','ASR','MMCT','21:30','00:05',84,84,1200.0,'Mail','duronto.jpg'),
        # GARIB RATH
        ('12909','Mumbai Bandra Garib Rath','BDTS','NDLS','15:10','09:45',96,96,650.0,'Garib Rath','duronto.jpg'),
        ('12203','Saharsa Garib Rath Express','SDAH','SVDK','21:35','04:00',96,96,600.0,'Garib Rath','duronto.jpg'),
        ('12215','Delhi Garib Rath Express','DEE','BPL','21:20','07:40',96,96,580.0,'Garib Rath','duronto.jpg'),
        # LOCAL - MUMBAI
        ('90001','Mumbai CST Thane Local','CSTM','TNA','06:00','06:45',300,300,20.0,'Local','shatabdi.jpg'),
        ('90002','Mumbai Borivali Fast Local','CSTM','BVI','06:15','07:30',300,300,25.0,'Local','shatabdi.jpg'),
        ('90003','Mumbai Khopoli Local','CSTM','KPL','07:00','10:15',300,300,55.0,'Local','shatabdi.jpg'),
        ('90004','Pune Lonavala Local','PUNE','LNL','06:30','08:15',250,250,35.0,'Local','shatabdi.jpg'),
        ('90005','Mumbai Kalyan Local','CSTM','KYN','07:30','08:45',300,300,30.0,'Local','shatabdi.jpg'),
        ('90006','Mumbai Virar Fast Local','CSTM','VR','08:00','09:30',300,300,30.0,'Local','shatabdi.jpg'),
        # LOCAL - KOLKATA
        ('90101','Howrah Burdwan Local','HWH','BWN','06:10','08:40',300,300,35.0,'Local','shatabdi.jpg'),
        ('90102','Sealdah Ranaghat Local','SDAH','RHA','06:30','08:45',300,300,40.0,'Local','shatabdi.jpg'),
        ('90103','Howrah Arambagh Local','HWH','ABG','07:15','10:00',250,250,50.0,'Local','shatabdi.jpg'),
        ('90104','Kolkata Barasat Local','KOAA','BT','07:00','08:00',300,300,25.0,'Local','shatabdi.jpg'),
        ('90105','Sealdah Diamond Harbour Local','SDAH','DMH','08:00','09:45',250,250,30.0,'Local','shatabdi.jpg'),
        # LOCAL - CHENNAI
        ('90201','Chennai Beach Tambaram Local','MSB','TBM','06:00','07:00',300,300,18.0,'Local','shatabdi.jpg'),
        ('90202','Chennai Central Chengalpattu','MAS','CGL','06:30','08:30',300,300,35.0,'Local','shatabdi.jpg'),
        ('90203','Chennai Avadi Local','MSB','AVD','07:00','08:15',300,300,22.0,'Local','shatabdi.jpg'),
        ('90204','Chennai Arakkonam Local','MAS','AJJ','07:30','09:30',300,300,38.0,'Local','shatabdi.jpg'),
        # LOCAL - HYDERABAD
        ('90301','Secunderabad Malkajgiri Local','SC','MJF','06:10','06:35',250,250,10.0,'Local','shatabdi.jpg'),
        ('90302','Hyderabad Lingampally Local','HYB','LPI','07:00','07:45',250,250,15.0,'Local','shatabdi.jpg'),
        ('90303','Secunderabad Falaknuma Local','SC','FM','06:30','07:15',250,250,12.0,'Local','shatabdi.jpg'),
        # LOCAL - BANGALORE
        ('90401','Bangalore Tumkur Local','SBC','TK','06:15','08:45',250,250,40.0,'Local','shatabdi.jpg'),
        ('90402','Bangalore Hosur Local','SBC','HOS','07:00','09:00',250,250,35.0,'Local','shatabdi.jpg'),
        ('90403','Mysore Bangalore Local','MYS','SBC','06:00','08:45',250,250,45.0,'Local','shatabdi.jpg'),
        # LOCAL - DELHI
        ('90501','Delhi Ghaziabad EMU','NDLS','GZB','06:00','06:45',300,300,20.0,'Local','shatabdi.jpg'),
        ('90502','Delhi Palwal EMU','NDLS','PWL','06:30','08:30',300,300,35.0,'Local','shatabdi.jpg'),
        ('90503','Delhi Rohtak EMU','NDLS','ROK','07:30','09:30',300,300,40.0,'Local','shatabdi.jpg'),
        ('90504','Delhi Faridabad EMU','NDLS','FDB','06:15','07:05',300,300,18.0,'Local','shatabdi.jpg'),
        # VILLAGE - UTTAR PRADESH
        ('55001','Lucknow Sitapur Passenger','LKO','STP','06:30','10:00',180,180,60.0,'Passenger','shatabdi.jpg'),
        ('55002','Varanasi Jaunpur Passenger','BSB','JNU','07:00','09:30',180,180,45.0,'Passenger','shatabdi.jpg'),
        ('55003','Gorakhpur Basti Passenger','GKP','BST','06:00','08:00',180,180,38.0,'Passenger','shatabdi.jpg'),
        ('55004','Allahabad Mirzapur Passenger','PRYJ','MZP','07:30','10:00',180,180,55.0,'Passenger','shatabdi.jpg'),
        ('55005','Agra Mathura Passenger','AGC','MTJ','06:00','07:30',180,180,30.0,'Passenger','shatabdi.jpg'),
        ('55006','Kanpur Fatehpur Passenger','CNB','FTP','07:00','09:00',180,180,40.0,'Passenger','shatabdi.jpg'),
        ('55007','Bareilly Shahjahanpur Passenger','BE','SPN','06:30','08:15',180,180,32.0,'Passenger','shatabdi.jpg'),
        ('55008','Meerut Modinagar Passenger','MTC','MDNR','06:00','06:45',180,180,18.0,'Passenger','shatabdi.jpg'),
        # VILLAGE - BIHAR
        ('55101','Patna Nalanda Passenger','PNBE','NLD','06:30','08:30',180,180,40.0,'Passenger','shatabdi.jpg'),
        ('55102','Gaya Bodhgaya Passenger','GAYA','BGYA','07:00','07:45',180,180,18.0,'Passenger','shatabdi.jpg'),
        ('55103','Muzaffarpur Sitamarhi Passenger','MFP','SMI','06:15','09:00',180,180,55.0,'Passenger','shatabdi.jpg'),
        ('55104','Bhagalpur Banka Passenger','BGP','BKA','07:30','10:00',180,180,50.0,'Passenger','shatabdi.jpg'),
        ('55105','Darbhanga Madhubani Passenger','DBG','MBI','06:00','08:00',180,180,40.0,'Passenger','shatabdi.jpg'),
        # VILLAGE - RAJASTHAN
        ('55201','Jaipur Sikar Passenger','JP','SIKR','07:00','09:30',180,180,50.0,'Passenger','shatabdi.jpg'),
        ('55202','Jodhpur Barmer Passenger','JU','BME','06:30','11:00',180,180,90.0,'Passenger','shatabdi.jpg'),
        ('55203','Udaipur Chittorgarh Passenger','UDZ','COR','07:00','09:15',180,180,45.0,'Passenger','shatabdi.jpg'),
        ('55204','Bikaner Suratgarh Passenger','BKN','SRTG','06:00','10:00',180,180,80.0,'Passenger','shatabdi.jpg'),
        ('55205','Ajmer Pushkar Passenger','AII','PSHK','07:30','08:30',180,180,20.0,'Passenger','shatabdi.jpg'),
        # VILLAGE - MADHYA PRADESH
        ('55301','Bhopal Vidisha Passenger','BPL','BHS','06:30','08:30',180,180,38.0,'Passenger','shatabdi.jpg'),
        ('55302','Indore Dewas Passenger','INDB','DWX','07:00','08:00',180,180,22.0,'Passenger','shatabdi.jpg'),
        ('55303','Jabalpur Katni Passenger','JBP','KTE','06:15','09:00',180,180,55.0,'Passenger','shatabdi.jpg'),
        ('55304','Gwalior Datia Passenger','GWL','DAA','07:30','08:45',180,180,28.0,'Passenger','shatabdi.jpg'),
        ('55305','Rewa Satna Passenger','REWA','STA','06:00','08:30',180,180,50.0,'Passenger','shatabdi.jpg'),
        # VILLAGE - WEST BENGAL
        ('55401','Kolkata Krishnanagar Passenger','KOAA','KNJ','07:00','09:30',180,180,50.0,'Passenger','shatabdi.jpg'),
        ('55402','Siliguri Jalpaiguri Passenger','SGUJ','JPG','06:30','08:00',180,180,32.0,'Passenger','shatabdi.jpg'),
        ('55403','Burdwan Katwa Passenger','BWN','KWA','07:15','09:00',180,180,38.0,'Passenger','shatabdi.jpg'),
        ('55404','Malda Balurghat Passenger','MLDT','BLGT','06:00','10:00',180,180,80.0,'Passenger','shatabdi.jpg'),
        # VILLAGE - TAMIL NADU
        ('55501','Madurai Dindigul Passenger','MDU','DG','06:30','08:30',180,180,40.0,'Passenger','shatabdi.jpg'),
        ('55502','Coimbatore Pollachi Passenger','CBE','POY','07:00','08:30',180,180,32.0,'Passenger','shatabdi.jpg'),
        ('55503','Salem Erode Passenger','SA','ED','06:15','07:45',180,180,30.0,'Passenger','shatabdi.jpg'),
        ('55504','Tirunelveli Nagercoil Passenger','TEN','NCJ','07:30','09:00',180,180,30.0,'Passenger','shatabdi.jpg'),
        ('55505','Trichy Thanjavur Passenger','TPJ','TJ','06:00','08:00',180,180,40.0,'Passenger','shatabdi.jpg'),
        ('55506','Chennai Kanchipuram Passenger','MAS','KPD','07:00','09:30',180,180,50.0,'Passenger','shatabdi.jpg'),
        # VILLAGE - KERALA
        ('55601','Thiruvananthapuram Kollam Pass','TVC','QLN','06:30','08:00',180,180,32.0,'Passenger','shatabdi.jpg'),
        ('55602','Ernakulam Thrissur Passenger','ERS','TCR','07:00','08:30',180,180,32.0,'Passenger','shatabdi.jpg'),
        ('55603','Kozhikode Kannur Passenger','CLT','CAN','06:15','08:15',180,180,40.0,'Passenger','shatabdi.jpg'),
        ('55604','Palakkad Pollachi Passenger','PGT','POY','07:30','09:30',180,180,40.0,'Passenger','shatabdi.jpg'),
        # VILLAGE - MAHARASHTRA
        ('55701','Nashik Igatpuri Passenger','NK','IGP','06:30','08:45',180,180,45.0,'Passenger','shatabdi.jpg'),
        ('55702','Aurangabad Jalgaon Passenger','AWB','JL','07:00','11:00',180,180,80.0,'Passenger','shatabdi.jpg'),
        ('55703','Kolhapur Sangli Passenger','KOP','SLI','06:00','08:00',180,180,40.0,'Passenger','shatabdi.jpg'),
        ('55704','Solapur Bijapur Passenger','SUR','BJP','07:30','11:00',180,180,70.0,'Passenger','shatabdi.jpg'),
        ('55705','Nanded Latur Passenger','NED','LUR','06:15','09:00',180,180,55.0,'Passenger','shatabdi.jpg'),
        ('55706','Amravati Akola Passenger','AMI','AK','07:00','09:30',180,180,50.0,'Passenger','shatabdi.jpg'),
        # VILLAGE - GUJARAT
        ('55801','Ahmedabad Mehsana Passenger','ADI','MSH','06:30','08:30',180,180,40.0,'Passenger','shatabdi.jpg'),
        ('55802','Surat Valsad Passenger','ST','BL','07:00','09:00',180,180,40.0,'Passenger','shatabdi.jpg'),
        ('55803','Rajkot Gondal Passenger','RJT','GNDL','06:15','07:45',180,180,30.0,'Passenger','shatabdi.jpg'),
        ('55804','Vadodara Anand Passenger','BRC','ANND','07:30','08:30',180,180,22.0,'Passenger','shatabdi.jpg'),
        ('55805','Bhavnagar Botad Passenger','BVC','BOT','06:00','08:30',180,180,50.0,'Passenger','shatabdi.jpg'),
        # VILLAGE - ODISHA
        ('55901','Bhubaneswar Cuttack Passenger','BBS','CTC','06:30','07:30',180,180,22.0,'Passenger','shatabdi.jpg'),
        ('55902','Puri Brahmapur Passenger','PURI','BAM','07:00','10:00',180,180,60.0,'Passenger','shatabdi.jpg'),
        ('55903','Sambalpur Rourkela Passenger','SBP','ROU','06:15','10:15',180,180,80.0,'Passenger','shatabdi.jpg'),
        # VILLAGE - PUNJAB / HARYANA
        ('56001','Amritsar Gurdaspur Passenger','ASR','GDP','06:30','08:30',180,180,40.0,'Passenger','shatabdi.jpg'),
        ('56002','Ludhiana Fatehgarh Sahib Pass','LDH','FGSH','07:00','08:30',180,180,30.0,'Passenger','shatabdi.jpg'),
        ('56003','Jalandhar Kapurthala Passenger','JUC','KPT','06:15','07:00',180,180,16.0,'Passenger','shatabdi.jpg'),
        ('56101','Ambala Kurukshetra Passenger','UMB','KRNT','06:30','08:00',180,180,32.0,'Passenger','shatabdi.jpg'),
        ('56102','Hisar Sirsa Passenger','HSR','SSA','07:00','09:30',180,180,50.0,'Passenger','shatabdi.jpg'),
        # HILL / TOY TRAINS
        ('59001','Darjeeling Himalayan Railway','NJP','DJ','07:00','12:00',80,80,350.0,'Toy Train','vande_bharat.jpg'),
        ('59002','Nilgiri Mountain Railway','MTP','OTY','07:10','10:40',80,80,280.0,'Toy Train','vande_bharat.jpg'),
        ('59003','Matheran Hill Railway','NERAL','MTN','08:40','11:10',80,80,200.0,'Toy Train','vande_bharat.jpg'),
        ('59004','Kalka Shimla Railway','KLK','SML','06:00','11:30',100,100,250.0,'Heritage','vande_bharat.jpg'),
        # NORTHEAST
        ('56401','Guwahati Jorhat Passenger','GHY','JRT','06:30','14:30',180,180,160.0,'Passenger','shatabdi.jpg'),
        ('56402','Dibrugarh Tinsukia Passenger','DBG','TSKT','07:00','08:30',180,180,30.0,'Passenger','shatabdi.jpg'),
        ('56403','Agartala Sabroom Passenger','AGTL','SBMR','07:30','12:30',120,120,100.0,'Passenger','shatabdi.jpg'),
        # JHARKHAND / CHHATTISGARH
        ('56501','Ranchi Hazaribagh Passenger','RNC','HZB','06:30','10:00',180,180,70.0,'Passenger','shatabdi.jpg'),
        ('56502','Jamshedpur Dhanbad Passenger','TATA','DHN','07:00','11:00',180,180,80.0,'Passenger','shatabdi.jpg'),
        ('56601','Raipur Durg Passenger','R','DURG','06:30','08:00',180,180,32.0,'Passenger','shatabdi.jpg'),
        ('56602','Bilaspur Korba Passenger','BSP','KRBA','07:00','10:00',180,180,60.0,'Passenger','shatabdi.jpg'),
        # HUMSAFAR / ANTYODAYA
        ('82651','Yesvantpur Humsafar Express','YPR','GKP','07:30','15:45',80,80,1150.0,'Humsafar','duronto.jpg'),
        ('82661','Bhagalpur Humsafar Express','BGP','BDTS','10:15','12:30',80,80,1200.0,'Humsafar','duronto.jpg'),
        ('22887','Antyodaya Express Howrah','HWH','PNBE','22:00','05:45',200,200,320.0,'Antyodaya','duronto.jpg'),
        ('22888','Antyodaya Express Patna','PNBE','HWH','21:30','05:15',200,200,320.0,'Antyodaya','duronto.jpg'),
    ]

    for t in trains:
        try:
            db.execute('''INSERT INTO trains (train_no,train_name,from_station,to_station,
               departure,arrival,total_seats,available_seats,price_per_seat,
               train_type,image) VALUES (?,?,?,?,?,?,?,?,?,?,?)''', t)
            print(f"  OK {t[0]} {t[1]}")
        except Exception as e:
            print(f"  SKIP {t[0]}: {e}")

    db.commit()
    db.close()

    print("\n" + "="*55)
    print(f"DONE! {len(trains)} trains + {len(users)} users added")
    print("="*55)
    print("Admin  : admin  / admin123")
    print("User 1 : rahul  / rahul123")
    print("User 2 : priya  / priya123")
    print("="*55)
    print("\nSTATION CODES REFERENCE:")
    codes = [
        "NDLS=New Delhi    HWH=Howrah        MAS=Chennai",
        "MMCT=Mumbai       SBC=Bengaluru     ADI=Ahmedabad",
        "LKO=Lucknow       BSB=Varanasi      GKP=Gorakhpur",
        "PUNE=Pune         SC=Secunderabad   VSKP=Vizag",
        "TVC=Trivandrum    BPL=Bhopal        ASR=Amritsar",
        "JP=Jaipur         JU=Jodhpur        UDZ=Udaipur",
        "MDU=Madurai       CBE=Coimbatore    ERS=Ernakulam",
        "CLT=Kozhikode     BBS=Bhubaneswar   RNC=Ranchi",
        "GHY=Guwahati      DBG=Dibrugarh     NJP=New Jalpaiguri",
    ]
    for c in codes:
        print("  " + c)

if __name__ == '__main__':
    seed()
