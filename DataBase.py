import psycopg2
import json


class DataBase:
    def __init__(self):
        self.__conn = psycopg2.connect(dbname='certif', user='certif',
                                       password='Qwe123q', host='95.163.236.190')
        with open("conf.json", "r") as read_file:
            self.__conf = json.load(read_file)

    def get_scans(self):
        cursor = self.__conn.cursor()
        cursor.execute("SELECT * FROM scans;")
        return cursor.fetchall()

    def make_scan(self):
        cursor = self.__conn.cursor()
        cursor.execute("INSERT INTO scans (data, time) VALUES (now(), now()) RETURNING id;")
        self.__conn.commit()
        return cursor.fetchall()[0][0]

    def get_cert(self, id):
        cursor = self.__conn.cursor()
        cursor.execute(f"""SELECT verdict, cryptAlgo, serialNumber, hash, lenghtOpenKey, 
        isdToWhom, WhoIsd, ValidUntil FROM cert WHERE scan = {id};""")
        return cursor.fetchall()

    def insert_cert(self, id, verdict, cryptAlgo, serialNumber, hash, lenghtOpenKey, isdToWhom, WhoIsd, ValidUntil):
        cursor = self.__conn.cursor()
        cursor.execute(f'''INSERT INTO cert (scan, verdict, cryptAlgo, serialNumber, hash, lenghtOpenKey, isdToWhom, 
        WhoIsd, ValidUntil) VALUES ({id},'{verdict}','{cryptAlgo}','{serialNumber}','{hash}','{lenghtOpenKey}',
        '{isdToWhom}','{WhoIsd}','{ValidUntil}');''')
        self.__conn.commit()

    def get_conf(self):
        return self.__conf

    def set_file_conf(self, conf):
        self.__conf = conf
        self.__save_conf()

    def set_conf(self, next_scan=None, scandelta=None, ip=None, port=None, ignore1Y=None, ignoreKL=None, ignoreNVC=None,
                 ignoreExc=None, ignoreAlgo=None, checkCenter=None, checkDate=None):
        if next_scan is not None:
            self.__conf["next_scan"] = next_scan
        if scandelta is not None:
            self.__conf["scandelta"] = scandelta
        if ip is not None:
            self.__conf["ip"] = ip
        if port is not None:
            self.__conf["port"] = port
        if ignore1Y is not None:
            self.__conf["ignore1y"] = ignore1Y
        if ignoreKL is not None:
            self.__conf["ignorekl"] = ignoreKL
        if ignoreNVC is not None:
            self.__conf["ignorenvc"] = ignoreNVC
        if ignoreExc is not None:
            self.__conf["ignoreexc"] = ignoreExc
        if ignoreAlgo is not None:
            self.__conf["ignorealgo"] = ignoreAlgo
        if checkCenter is not None:
            self.__conf["checkcenter"] = checkCenter
        if checkDate is not None:
            self.__conf["checkdate"] = checkDate
        print(self.__conf)
        self.__save_conf()

    def __save_conf(self):
        with open("conf.json", "w") as write_file:
            json.dump(self.__conf, write_file)

    def insert_user(self, teleid):
        cursor = self.__conn.cursor()
        try:
            cursor.execute(f"INSERT INTO users (teleid) VALUES ('{teleid}')")
        except psycopg2.Error:
            print("duplicate user")
        self.__conn.commit()

    def delete_user(self, teleid):
        cursor = self.__conn.cursor()
        cursor.execute(f"DELETE FROM users WHERE teleid='{teleid}'")
        self.__conn.commit()

    def get_user_list(self):
        cursor = self.__conn.cursor()
        cursor.execute(f"SELECT teleid FROM users")
        return [i[0] for i in cursor.fetchall()]

    def add_sign_center(self, comp):
        cursor = self.__conn.cursor()
        cursor.execute(f"INSERT INTO certlist (com) VALUES ('{comp}');")
        self.__conn.commit()

    def get_sign_center_list(self):
        cursor = self.__conn.cursor()
        cursor.execute(f"SELECT com FROM certlist;")
        return [i[0] for i in cursor.fetchall()]
