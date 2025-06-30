from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from tools import GeneralRequest
from kivy.network.urlrequest import UrlRequest
from kivy.app import App
from datetime import datetime
import json


class AnnouncementScreen(MDScreen):
    def on_enter(self):
        self.app = App.get_running_app()
        self.clear_inputs()
        self.get_announcements = lambda: GeneralRequest(self.app.base_url + 'api/announcement/announcements', req_headers={"Content-Type" : "application/json",'Authorization': f'Bearer {self.app.access}'}, on_success=self.got_announcements, refresh=self.app.refresh)
        self.get_announcements()

    def got_announcements(self, request, result):
        self.ids.container.clear_widgets()
        for announcement in result:
            d = datetime.fromisoformat(announcement.get('updated_at'))
            announcementComponent = AnnouncementComponent()
            announcementComponent.set_details(announcement.get('id'), announcement.get('title'), announcement.get('content'), d.date().isoformat(), self.get_announcements)
            self.ids.container.add_widget(announcementComponent)
    
    def post_announcement(self):
        title = self.ids.title.text
        details = self.ids.details.text
        GeneralRequest(
            self.app.base_url + 'api/announcement/announcements', 
            req_body=json.dumps({'title': title, 'content': details}), 
            req_headers={"Content-Type" : "application/json",'Authorization': f'Bearer {self.app.access}'}, 
            on_success=lambda request, result: self.clear_inputs(), 
            refresh=self.app.refresh
        )
    
    def clear_inputs(self):
        self.ids.title.text = ''
        self.ids.details.text = ''



class AnnouncementComponent(MDBoxLayout):
    def set_details(self, id, title, details, date, get_announcements):
        self.announcement_id = id
        self.ids.title.text = title
        self.ids.details.text = details
        self.ids.date.text = date
        self.get_announcements = get_announcements
    
    def delete(self):
        app = App.get_running_app()
        UrlRequest(
            app.base_url + f'api/announcement/announcement/{str(self.announcement_id)}', 
            req_headers={"Content-Type" : "application/json",'Authorization': f'Bearer {app.access}'}, method='DELETE',
            on_success=lambda request, result: self.get_announcements()
            )
