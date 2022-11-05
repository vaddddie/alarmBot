import datetime
import sqlite3

class Filler:
    data = {
        1: 31,
        2: 28,
        3: 31,
        4: 30,
        5: 31,
        6: 30,
        7: 31,
        8: 31,
        9: 30,
        10: 31,
        11: 30,
        12: 31,
    }

    def __init__(self):
        self.connection = sqlite3.connect("DATABASE.db")
        self.cursor = self.connection.cursor()

    def write_base(self, chat_id, month, init_day=1, fine=False, room=-1, exception=False):
        if self.check_the_table(month, chat_id):
            self.delete_the_table(month, chat_id)
        self.create_the_table(month, chat_id)

        if init_day > self.get_days_n(month):
            init_day = 1

        if month > 12:
            month = 1

        if fine:
            self.write_with_fine(month, chat_id, init_day, room, exception)
        else:
            self.write(month, chat_id, init_day)


    def write(self, month, chat_id, init_day):
        pre_month = month - 1
        if pre_month == 0:
            pre_month = 12
        if self.check_the_table(pre_month, chat_id):
            rm = self.get_last_room(pre_month, chat_id)
            for i in range(init_day, self.get_days_n(month) + 1):
                rm += 1
                if rm == self.get_rooms_n(chat_id) + 1:
                    rm = 1
                self.cursor.execute(f"INSERT INTO '{month}_graph_{chat_id}' VALUES ({i}, {rm}, {1})")
                self.connection.commit()
        else:
            rm = 0
            for i in range(init_day, self.get_days_n(month) + 1):
                rm += 1
                if rm == self.get_rooms_n(chat_id) + 1:
                    rm = 1
                self.cursor.execute(f"INSERT INTO '{month}_graph_{chat_id}' VALUES ({i}, {rm}, {1})")
                self.connection.commit()


    def write_with_fine(self, month, chat_id, init_day, room, exception):
        if not exception:
            self.cursor.execute(f"INSERT INTO '{month}_graph_{chat_id}' VALUES ({init_day}, {room}, {1})")
            self.connection.commit()
            init_day += 1
        rm = room - 1
        for i in range(init_day, self.get_days_n(month) + 1):
            rm += 1
            if rm == self.get_rooms_n(chat_id) + 1:
                rm = 1
            self.cursor.execute(f"INSERT INTO '{month}_graph_{chat_id}' VALUES ({i}, {rm}, {1})")
            self.connection.commit()

    def write_one_day(self, month, chat_id, init_day, room):
        self.cursor.execute(f"INSERT INTO '{month}_graph_{chat_id}' VALUES ({init_day}, {room}, {1})")
        self.connection.commit()

    def check_the_table(self, month, chat_id):
        return self.cursor.execute(f"""
                                   SELECT name FROM sqlite_master WHERE type='table' AND name='{month}_graph_{chat_id}'
                               """).fetchone() is not None

    def create_the_table(self, month, chat_id):
        self.cursor.execute(f"CREATE TABLE '{month}_graph_{chat_id}'(day, id, boolean)")

    def delete_the_table(self, month, chat_id):
        self.cursor.execute(f"DROP TABLE '{month}_graph_{chat_id}'")

    def get_rooms_n(self, chat_id):
        return self.cursor.execute(f"SELECT COUNT(*) FROM '{chat_id}_members'").fetchone()[0]

    def get_last_room(self, month, chat_id):
        day = self.get_days_n(month)
        return self.cursor.execute(f"SELECT id FROM '{month}_graph_{chat_id}' WHERE day={day}").fetchone()[0]

    def get_days_n(self, month):
        if month == 2 and datetime.datetime.now().year % 4 == 0:
            days_n = 29
        else:
            days_n = self.data[month]
        return days_n


