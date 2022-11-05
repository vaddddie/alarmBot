import datetime

from vk_api.utils import get_random_id
import sqlite3
import random
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from filler import Filler


time_zone = -3

class Alarm_bot:
    dictionary = [
        'Убрались',
        'Убралась',
        'Убрался',
        'Убрано',
        'Продежурили',
        'Отдежурили',
        'Продежурил',
        'Отдежурил',
        'Продежурила',
        'Отдежурила',
        'убрались',
        'убралась',
        'убрался',
        'убрано',
        'продежурили',
        'отдежурили',
        'продежурил',
        'отдежурил',
        'продежурила',
        'отдежурила',
    ]

    months = {
        1: 'ЯНВАРЬ',
        2: 'ФЕВРАЛЬ',
        3: 'МАРТ',
        4: 'АПРЕЛЬ',
        5: 'МАЙ',
        6: 'ИЮНЬ',
        7: 'ИЮЛЬ',
        8: 'АВГУСТ',
        9: 'СЕНТЯБРЬ',
        10: 'ОКТЯБРЬ',
        11: 'НОЯБРЬ',
        12: 'ДЕКАБРЬ',
    }

    def __init__(self, vk):
        self.filler = Filler()
        self.vk = vk

        self.connection = sqlite3.connect("DATABASE.db")
        self.cursor = self.connection.cursor()

    # ===========================================================================
    # ======================== General operations ===============================
    # ===========================================================================

    def send_message(self, user_id, chat_id, message, keyboard=None):
        self.vk.method('messages.send', {
            'user_id': user_id,
            'chat_id': chat_id,
            'message': message,
            'keyboard': keyboard,
            'random_id': get_random_id()
        })

    def server_input(self, event):
        if event.from_chat:
            message = event.object['message']
            chat_id = event.chat_id

            if message['text'] == '[club216564183|@alarm__bot] старт':
                self.start(message['from_id'], chat_id)

            elif message['text'] == '[club216564183|@alarm__bot] новое расписание':
                self.set_new_schedule(chat_id)

            elif message['text'] == '[club216564183|@alarm__bot] расписание':
                self.schedule(chat_id)

            elif message['text'] == '[club216564183|@alarm__bot] 5 утра':
                self.CHECKING()

            elif message['text'] == '[club216564183|@alarm__bot] 10 вечера':
                self.mailing()

            else:
                for item in message['text'].split(' '):
                    for word in self.dictionary:
                        if item == word:
                            self.duty(chat_id)

        if event.from_user:
            self.check_path(event.user_id)
            path = self.get_path(event.user_id)

            match path:
                case 0:
                    self.first_screen_view(event.user_id)
                case 1:
                    match event.text:
                        case 'Начать работу':
                            self.auth_screen_view(event.user_id)
                        case 'Помощь':
                            self.first_screen_view(event.user_id, message='Эта функция в разработке')
                        case 'О нас':
                            self.first_screen_view(event.user_id, message='Эта функция в разработке')
                        case _:
                            self.first_screen_view(event.user_id, message='Попробуй ещё :)')
                case 2:
                    if event.text == 'Назад':
                        self.first_screen_view(event.user_id, message='Зачем?')
                    else:
                        self.auth(event.user_id, event.text)
                case 3:
                    group_id = self.get_group_id(event.user_id)
                    if group_id:
                        match event.text:
                            case 'Добавить новую комнату':
                                if not self.check_table(group_id):
                                    self.create_new_table(group_id)
                                self.add_new_room_view(event.user_id)
                            case 'Удалить комнату':
                                self.manage_screen_view(event.user_id, message='Эта функция в разработке')
                            case 'Удалить всё':
                                self.delete_table(group_id)
                                self.create_new_table(group_id)
                                self.manage_screen_view(event.user_id, message='Успешно!')
                            case 'Назад':
                                self.first_screen_view(event.user_id, message='Что на этот раз?')
                            case _:
                                self.manage_screen_view(event.user_id, message='Ты уверен?')
                case 4:
                    group_id = self.get_group_id(event.user_id)
                    if group_id:
                        if event.text == 'Назад':
                            self.manage_screen_view(event.user_id, message='Что дальше?')
                        else:
                            self.new_room(event, group_id)





    @staticmethod
    def generator():
        chars = list('+-/*!$?=@abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')
        key = 'key#'
        key += ''.join([random.choice(chars) for x in range(15)])
        return key # Добавить проверку на наличия(а мало ли_))

    # ===========================================================================
    # ======================== ================== ===============================
    # ===========================================================================

    # ===========================================================================
    # ============================== Chat_bot ===================================
    # ===========================================================================

    # ============================= Check table chats ===========================

    def check_table_chats(self):
        if self.cursor.execute("""
                                SELECT name FROM sqlite_master WHERE type='table' AND name='paths'
                               """).fetchone() is None:
            self.cursor.execute("CREATE TABLE paths(user_id, path)")

    # ============================= Registration new table ======================

    def delete_table(self, chat_id):
        if self.cursor.execute(f"""
                                SELECT name FROM sqlite_master WHERE type='table' AND name='{chat_id}_members'
                               """).fetchone() is not None:
            self.cursor.execute(f"DROP TABLE '{chat_id}_members'")

    def check_table(self, chat_id):
        return self.cursor.execute(f"""
                                SELECT name FROM sqlite_master WHERE type='table' AND name='{chat_id}_members'
                               """).fetchone() is not None

    def create_new_table(self, chat_id):
        self.cursor.execute(f"CREATE TABLE '{chat_id}_members'(id, room_number, members)")

    # ====================================== Paths ==============================

    def check_path(self, user_id):
        if self.cursor.execute(f"SELECT * FROM paths WHERE user_id = {user_id}").fetchone() is None:
            self.cursor.execute(f"INSERT INTO paths VALUES ({user_id}, {0})")
            self.connection.commit()

    def get_path(self, user_id):
        return self.cursor.execute(f"SELECT path FROM paths WHERE user_id = {user_id}").fetchone()[0]

    def change_path(self, user_id, new_path):
        self.cursor.execute(f"UPDATE paths SET path = {new_path} WHERE user_id = {user_id}")
        self.connection.commit()

    # ============================ Views and keyboards ==========================

    def first_screen_view(self, user_id, message='Давайте начнем:'):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button(label='Начать работу', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button(label='Помощь', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button(label='О нас', color=VkKeyboardColor.SECONDARY)

        self.change_path(user_id, 1)
        self.send_message(user_id, None, message, keyboard.get_keyboard())

    def auth_screen_view(self, user_id):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button(label='Назад', color=VkKeyboardColor.NEGATIVE)

        self.change_path(user_id, 2)
        self.send_message(user_id, None, 'Введите ключ:', keyboard.get_keyboard())

    def manage_screen_view(self, user_id, message='Успешно!\nЧто дальше?'):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button(label='Добавить новую комнату', color=VkKeyboardColor.POSITIVE)

        keyboard.add_line()
        keyboard.add_button(label='Удалить комнату', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_button(label='Удалить всё', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_button(label='Назад', color=VkKeyboardColor.NEGATIVE)

        self.change_path(user_id, 3)
        self.send_message(user_id, None, message, keyboard.get_keyboard())



    def add_new_room_view(self, user_id, message='Введите "комнта/имена":'):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button(label='Назад', color=VkKeyboardColor.NEGATIVE)

        self.change_path(user_id, 4)
        self.send_message(user_id, None, message, keyboard.get_keyboard())

    def new_room(self, event, chat_id):
        try:
            message = event.text.split('/')
            self.insert_in_table(chat_id, message[0], message[1])

            self.add_new_room_view(event.user_id, 'Успешно! Следующий')
        except IndexError:
            self.add_new_room_view(event.user_id, 'Некорректный ввод. Попробуй ещё раз')

    # ============================= Other functions =============================

    def insert_in_table(self, chat_id, room_number, members):
        members_id = self.cursor.execute(f"SELECT COUNT(*) FROM '{chat_id}_members'").fetchone()[0]
        self.cursor.execute(f"INSERT INTO '{chat_id}_members' VALUES ({members_id + 1}, '{room_number}', '{members}')")
        self.connection.commit()

    def auth(self, user_id, key):
        if self.cursor.execute(f"SELECT * FROM groups WHERE key = '{key}'").fetchone() is not None:
            if self.cursor.execute(f"SELECT * FROM groups WHERE auth_person = {user_id}").fetchone() is not None:
                self.cursor.execute(f"UPDATE groups SET auth_person = {-1} WHERE auth_person = {user_id}")
            self.cursor.execute(f"UPDATE groups SET auth_person = {user_id} WHERE key = '{key}'")
            self.connection.commit()
            self.manage_screen_view(user_id)
        else:
            self.send_message(user_id, None, 'Такого ключа у нас нету(')
            self.auth_screen_view(user_id)

    def get_group_id(self, user_id):
        if self.cursor.execute(f"SELECT * FROM groups WHERE auth_person = {user_id}").fetchone() is not None:
            return self.cursor.execute(f"SELECT id FROM groups WHERE auth_person = {user_id}").fetchone()[0]
        else:
            self.first_screen_view(user_id)
            return False

    def set_new_schedule(self, chat_id):
        init_day = datetime.datetime.now().day
        month = datetime.datetime.now().month
        self.filler.write_base(chat_id, month=month, init_day=init_day)
        self.filler.write_base(chat_id, month=month + 1)

        self.send_message(None, chat_id, 'Ну допустим..')

    def duty(self, chat_id):
        if datetime.datetime.now().hour < 5 + time_zone:
            day = datetime.datetime.now().day - 1
            if day == 0:
                month = datetime.datetime.now().month - 1
                if month == 0:
                    month = 12
                day = self.filler.get_days_n(month)
            else:
                month = datetime.datetime.now().month
        else:
            day = datetime.datetime.now().day
            month = datetime.datetime.now().month
        self.cursor.execute(f"UPDATE '{month}_graph_{chat_id}' SET boolean = {0} WHERE day = {day}")
        self.connection.commit()
        self.send_message(None, chat_id, 'Записал')

    def CHECKING(self):
        data = []
        self.cursor.execute(f"SELECT id FROM groups")
        iterator = self.cursor.fetchone()
        while iterator:
            data.append(iterator[0])
            iterator = self.cursor.fetchone()

        for item in data:
            day = datetime.datetime.now().day - 1
            month = datetime.datetime.now().month
            if day == 0:
                month -= 1
                if month == 0:
                    month = 12
                day = self.filler.get_days_n(month)

            if self.filler.check_the_table(month, item):
                try:
                    if self.cursor.execute(f"SELECT boolean FROM '{month}_graph_{item}' WHERE day={day}").fetchone()[0] == 1:
                        room = self.cursor.execute(f"SELECT room_number FROM '{month}_graph_{item}' WHERE day={day}").fetchone()[0]
                        ID = self.cursor.execute(f"SELECT id FROM '{month}_graph_{item}' WHERE day={day}").fetchone()[0]
                        self.send_message(None, chat_id=item, message=f'Штрафные дни для комнаты {room}')
                        if datetime.datetime.now().day == self.filler.get_days_n(datetime.datetime.now().month):
                            self.filler.write_one_day(datetime.datetime.now().month, item, datetime.datetime.now().day, ID)
                            self.filler.write_base(item, datetime.datetime.now().month + 1, datetime.datetime.now().day, fine=True, room=ID, exception=True)
                        else:
                            self.filler.write_base(item, datetime.datetime.now().month, datetime.datetime.now().day, fine=True, room=ID)
                            self.filler.write_base(item, datetime.datetime.now().month + 1, datetime.datetime.now().day)
                except TypeError:
                    pass


    def mailing(self):
        data = []
        self.cursor.execute(f"SELECT id FROM groups")
        iterator = self.cursor.fetchone()
        while iterator:
            data.append(iterator[0])
            iterator = self.cursor.fetchone()

        for item in data:
            month = datetime.datetime.now().month
            day = datetime.datetime.now().day
            if datetime.datetime.now().day == 28:
                self.filler.write_base(item, month=month + 2)
            if self.filler.check_the_table(month, item):
                try:
                    if self.cursor.execute(f"SELECT boolean FROM '{month}_graph_{item}' WHERE day={day}").fetchone()[0] == 1:
                        id_ = self.cursor.execute(f"SELECT id FROM '{month}_graph_{item}' WHERE day={day}").fetchone()[0]
                        room = self.cursor.execute(f"SELECT room_number FROM '{item}_members' WHERE id={id_}").fetchone()[0]
                        message = self.cursor.execute(f"SELECT members FROM '{item}_members' WHERE id={id_}").fetchone()[0]
                        self.send_message(None, item, f'Сегодня дежурит {room} комната.\n{message}')
                except TypeError:
                    self.send_message(None, item, 'Попробуйте пересоздать расписание.')


    def schedule(self, chat_id):
        message = ''

        if not self.filler.check_the_table(datetime.datetime.now().month, chat_id):
            self.set_new_schedule(chat_id)

        message += f"{self.months[datetime.datetime.now().month]}\n"

        tmp = []

        self.cursor.execute(f"SELECT day FROM '{datetime.datetime.now().month}_graph_{chat_id}'")
        iterator = self.cursor.fetchone()
        while iterator:
            tmp.append(iterator[0])
            iterator = self.cursor.fetchone()

        for i in tmp:
            ID = self.cursor.execute(f"SELECT id FROM '{datetime.datetime.now().month}_graph_{chat_id}' WHERE day={i}").fetchone()[0]
            room = self.cursor.execute(f"SELECT room_number FROM '{chat_id}_members' WHERE id={ID}").fetchone()[0]
            message += f"{i} - {room}\n"

        next_month = datetime.datetime.now().month + 1

        if next_month == 13:
            next_month = 1

        message += f"\n\n{self.months[next_month]}\n"

        tmp = []

        self.cursor.execute(f"SELECT day FROM '{next_month}_graph_{chat_id}'")
        iterator = self.cursor.fetchone()
        while iterator:
            tmp.append(iterator[0])
            iterator = self.cursor.fetchone()

        for i in tmp:
            ID = self.cursor.execute(
                f"SELECT id FROM '{next_month}_graph_{chat_id}' WHERE day={i}").fetchone()[0]
            room = self.cursor.execute(f"SELECT room_number FROM '{chat_id}_members' WHERE id={ID}").fetchone()[0]
            message += f"{i} - {room}\n"


        self.send_message(None, chat_id, message)

    # ===========================================================================
    # ======================== ================== ===============================
    # ===========================================================================

    # ===========================================================================
    # ============================== Group_bot ===================================
    # ===========================================================================

    # ================================ Auth table ===============================
    def check_table_groups(self):
        if self.cursor.execute("""
                                SELECT name FROM sqlite_master WHERE type='table' AND name='groups'
                               """).fetchone() is None:
            self.cursor.execute("CREATE TABLE groups(id, key, auth_person)")
    # ===========================================================================

    def start(self, user_id, chat_id):
        self.send_message(None, chat_id, 'Процесс регистрации...')
        key = self.generator()

        if self.cursor.execute(f"SELECT * FROM groups WHERE id = {chat_id}").fetchone() is not None:
            self.cursor.execute(f"DELETE FROM groups WHERE id = {chat_id}")

        self.cursor.execute(f"INSERT INTO groups VALUES ({chat_id}, '{key}', {user_id})")
        self.connection.commit()

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button(label='Начать', color=VkKeyboardColor.POSITIVE)

        self.change_path(user_id, 0)

        self.send_message(user_id, None, f'''
                                              Привет!
                                              Я здесь, чтобы выдать тебе ключ от твоей беседы. Держи! :)\n
                                              Ключ: {key}\n
                                              Используй это чтобы настроить бота прямо здесь.
                                          ''', keyboard=keyboard.get_keyboard())
        self.send_message(None, chat_id, 'Успешно!')









"""
self.cursor.execute("INSERT INTO groups VALUES (2, 'fdf', 'sdfsdf')")
self.connection.commit()
print(self.cursor.execute(f"SELECT * FROM groups WHERE id = {1}").fetchone())
self.cursor.execute(f"DELETE FROM groups WHERE id = {1}")
print(self.cursor.execute(f"SELECT * FROM groups WHERE id = {1}").fetchone())
"""

# Проверить кик из беседы