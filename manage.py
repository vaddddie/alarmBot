from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.longpoll import VkLongPoll, VkEventType
from multiprocessing import Process
from run_class import Run_server_class
import timer
import time


vk_group_id = '216564183'
time_ = 22
duty_time = 5
time_zone = -3


class Run_server(Run_server_class):
    def __init__(self):
        super().__init__()
        self.bot.check_table_chats()
        self.long_poll = VkLongPoll(self.vk)

    def Run(self):
        for event in self.long_poll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.from_user and event.to_me:
                self.bot.server_input(event)


class Run_server_only_chats(Run_server_class):
    def __init__(self):
        super().__init__()
        self.bot.check_table_groups()
        self.long_poll = VkBotLongPoll(self.vk, vk_group_id)
        self.timer = timer.Timer(time_ + time_zone)
        self.timer_on_duty = timer.Timer(duty_time + time_zone)
        Process(target=self.StartTimer).start()
        Process(target=self.StartDutyTimer).start()

    def Run(self):
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat:
                self.bot.server_input(event)

    def StartTimer(self):
        self.timer.Time_calculations()
        while True:
            if self.timer.First_iter_step():
                Process(target=self.Run_timer).start()
                break

    def Run_timer(self):
        while True:
            if self.timer.Run_step():
                self.bot.mailing()
                time.sleep(23 * 60 * 60 + 59 * 60)

    def StartDutyTimer(self):
        self.timer_on_duty.Time_calculations()
        while True:
            if self.timer_on_duty.First_iter_step():
                Process(target=self.Run_duty_timer).start()
                break

    def Run_duty_timer(self):
        while True:
            if self.timer_on_duty.Run_step():
                self.bot.CHECKING()
                time.sleep(23 * 60 * 60 + 59 * 60)


class Management:
    def __init__(self):
        self.session = Run_server()
        self.session_chats = Run_server_only_chats()

        Process(target=self.session.Run).start()
        Process(target=self.session_chats.Run).start()


if __name__ == '__main__':
    server = Management()
