import sqlite3

con = sqlite3.connect(r"D:\docker\xhs\xhs\xhs.db")

class SQL_UTILS:

    LOCAL = "local"

    ADD = "add"
    @staticmethod
    def insert_data( name, data, type):
        name = name.replace("'", "")
        sql = f"INSERT INTO 'add' ('name', 'data', 'type') VALUES ('{name}', '{data}','{type}');"
        cur = con.cursor()
        cur.execute(sql)
        con.commit()
    @staticmethod
    def get_data( name, type):
        name = name.replace("'", "")
        sql = f"select * from 'add' where name = '{name}' and type = '{type}'";
        cur = con.cursor()
        cur.execute(sql)
        return cur.fetchall()

    @staticmethod
    def contains( name, type):
        name = name.replace("'", "")
        sql = f"select * from 'add' where name = '{name}' and type = '{type}'";
        cur = con.cursor()
        cur.execute(sql)
        return cur.fetchall().__len__() > 0

    @staticmethod
    def get_follow(user_id):
        sql = f"select * from 'follow' where name = '{user_id}'";
        cur = con.cursor()
        cur.execute(sql)
        data = cur.fetchall()
        if data.__len__() > 0:
            return data[0][1]
        else:
            return None
    @staticmethod
    def set_new_follow(user_id, note_id):
        sql = f"update 'follow' set value = '{note_id}' where name = '{user_id}'";
        cur = con.cursor()
        cur.execute(sql)
        con.commit()

    @staticmethod
    def insert_new_follow(user_id, note_id):
        sql = f"INSERT INTO 'follow' ('name', 'value') VALUES ('{user_id}', '{note_id}');"
        cur = con.cursor()
        cur.execute(sql)
        con.commit()

if __name__ == '__main__':
    print(SQL_UTILS.set_new_follow("11", "232"))