from kivymd.uix.screen import MDScreen
from kivy.app import App
from kivy.network.urlrequest import UrlRequest, UrlRequestUrllib
from kivy.resources import resource_find
from tools import GeneralRequest
import json


class MainScreen(MDScreen):
    def on_enter(self):
        self.app = App.get_running_app()
    
    def login(self):
        username = self.ids.username.text
        password = self.ids.password.text
        GeneralRequest(self.app.base_url + 'api/account/token', req_body=json.dumps({'username': username, 'password': password}), req_headers={"Content-Type" : "application/json"}, on_success=self.on_successful_login)
    
    def on_successful_login(self, request:UrlRequestUrllib, result:dict):
        self.app.access = result.get('access')
        self.app.refresh = result.get('refresh')
        with open(resource_find('./token.json'), 'w') as f:
            f.write(json.dumps({'refresh': result.get('refresh')}))
        self.app.sm.current = 'home_screen'
            
