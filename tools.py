from kivy.app import App
from kivy.network.urlrequest import UrlRequest, UrlRequestUrllib
from kivy.metrics import dp
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.uix.modalview import ModalView
from kivymd.uix.spinner import MDSpinner
from typing import Callable
import json

class GeneralRequest:
    def __init__(self, url:str, req_body:str=None, req_headers:dict=None, on_success:Callable=None, refresh:str=None, on_finish:Callable=None):
        self.own_finish = on_finish
        self.refresh = refresh
        UrlRequest(url, req_body=req_body, req_headers=req_headers, on_success=on_success, on_finish=lambda request: self.on_finish(request))
        self.dialog = ModalView(background = '', background_color = (0, 0, 0, 0))
        self.dialog.add_widget(MDSpinner(active=True, size_hint=(None, None), size=(dp(46), dp(46)), line_width = dp(3.3), palette=[[234/255, 68/255, 68/255, 1]]))
        self.dialog.open()
    
    def on_finish(self, request:UrlRequestUrllib):
        status = request.resp_status
        if (status == 403):
            app = App.get_running_app()
            app.log_out()
        elif (status == 401):
            print('Refreshing access token')
            if (self.refresh):
                UrlRequest(
                    'https://triple-j.onrender.com/api/account/token/refresh', on_success=lambda request, result: self.on_refresh(request, result), 
                    req_body=json.dumps({'refresh': self.refresh}), req_headers={"Content-Type" : "application/json"}
                    )
        
        if (self.own_finish):
            self.own_finish(request)
        
        self.dialog.dismiss()
    
    def on_refresh(self, request:UrlRequestUrllib, result):
        app = App.get_running_app()
        app.access = result.get('access')
        print('Access token refreshed')


class SpinnerContent(MDFloatLayout):
    pass
