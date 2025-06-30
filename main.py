from kivy.core.window import Window
from kivy.config import Config
Config.set('kivy','window_icon','logo.ico')
Window.size = (1080, 720)
Window.minimum_width, Window.minimum_height = 1080, 720
from kivymd.app import MDApp, App
from kivy.lang import Builder
from kivymd.uix.screenmanager import MDScreenManager
from kivy.resources import resource_find, resource_add_path
from controller.main_screen import MainScreen
from controller.home_screen import HomeScreen
from controller.annoucement_screen import AnnouncementScreen
from controller.analytics_screen import AnalyticsScreen
from controller.member_screen import MemberScreen
from kivy.network.urlrequest import UrlRequestUrllib
from tools import GeneralRequest
import json
import sys
import os


def load_kv_files():
    design_files = ['./components.kv','./design/main.kv', './design/home.kv', './design/announcement.kv', './design/analytics.kv', './design/member.kv']
    for design_file in design_files:
        Builder.load_file(resource_find(design_file))


class TripleJAdmin(MDApp):
    base_url = 'https://triple-j.onrender.com/'
    access = None
    refresh = None
    theme = {
        'primary': (49/255, 48/255, 48/255, 1),
        'secondary': (30/255, 31/255, 38/255, 1),
        'tertiary': (94/255, 92/255, 92/255, 1),
        'accent': (234/255, 68/255, 68/255, 1),
        'green': (118/255, 208/255, 156/255, 1),
        'violet': (81/255, 71/255, 222/255, 1)
    }

    def build(self):
        self.sm = MDScreenManager()
        mainScreen = MainScreen(name='main_screen')
        self.sm.add_widget(mainScreen)
        homeScreen = HomeScreen(name='home_screen')
        self.sm.add_widget(homeScreen)
        announcementScreen = AnnouncementScreen(name='announcement_screen')
        self.sm.add_widget(announcementScreen)
        analyticsScreen = AnalyticsScreen(name='analytics_screen')
        self.sm.add_widget(analyticsScreen)
        memberScreen = MemberScreen(name='member_screen')
        self.sm.add_widget(memberScreen)
        self.sm.current = 'main_screen'
        return self.sm

    def on_start(self):
        try:
            with open(resource_find('./token.json'), 'r') as f:
                content = f.read()
                if (not content):
                    return
                token = json.loads(content).get('refresh')
                if (token):
                    self.refresh = token
                    GeneralRequest(self.base_url + 'api/account/token/refresh', json.dumps({'refresh': token}), {"Content-Type" : "application/json"}, self.log_in)
        except FileNotFoundError:
            print('no token!')
        return super().on_start()

    def log_in(self, request:UrlRequestUrllib, result:dict):
        self.access = result.get('access')
        self.sm.current = 'home_screen'
    
    def log_out(self):
        try:
            with open(resource_find('./token.json'), 'w') as f:
                f.write('')
        except FileNotFoundError:
            print('No Token')
        self.sm.current = 'main_screen'
    

if __name__ == "__main__":
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    load_kv_files()
    TripleJAdmin().run()

