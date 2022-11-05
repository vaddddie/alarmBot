import vk_api
from environs import Env
from alarm_bot import Alarm_bot


env = Env()
env.read_env()


class Run_server_class:
    def __init__(self):
        self.token = env('SECRET_KEY')
        self.vk = vk_api.VkApi(token=self.token)
        self.bot = Alarm_bot(self.vk)
