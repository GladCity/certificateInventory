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
        cursor.execute("INSERT INTO scans (data, time) VALUES (now(), now());")
        self.__conn.commit()

    def get_cert(self, id):
        pass
        # cursor = self.__conn.cursor()
        # cursor.execute(f"SELECT  FROM cert WHERE scan = {id};")
        # return cursor.fetchall()

    def insert_cert(self, id):
        pass
        # cursor = self.__conn.cursor()
        # cursor.execute(f"INSERT INTO cert (scan, ) VALUES ({id}, )")

    def get_conf(self):
        return self.__conf

    def set_conf(self, next_scan, scandelta, ip):
        self.__conf["next_scan"] = next_scan
        self.__conf["scandelta"] = scandelta
        self.__conf["ip"] = ip

    def save_conf(self):
        with open("conf.json", "w") as write_file:
            json.dump(self.__conf, write_file)

    def insert_user(self, teleid):
        cursor = self.__conn.cursor()
        cursor.execute(f"INSERT INTO users (teleid) VALUES ('{teleid}')")
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


if __name__ == "__main__":
    db = DataBase()

    print([str(i[0]) + ") " + str(i[1]) + " " + str(i[2]).split(".")[0] for i in db.get_scans()])
    print(list(db.get_sign_center_list()))
