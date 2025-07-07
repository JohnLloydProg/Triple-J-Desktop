from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.behaviors import HoverBehavior
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequestUrllib
from tools import GeneralRequest
from kivy.app import App
import json

"""
{
    'id': 4, 
    'username': 'its_louis', 'first_name': 'Louis', 'last_name': 'Gascon', 
    'email': 'spadewashere20@gmail.com', 'birthDate': '2001-02-22', 'height': 176.0, 
    'weight': 62.0, 'mobileNumber': '0917999890', 'address': '1050 Metro-apartment', 
    'gymTrainer': None, 'sex': 'Male', 'profilePic': None
}
"""

class MemberScreen(MDScreen):
    searched = False

    def on_enter(self):
        self.app = App.get_running_app()
        self.get_members = lambda: GeneralRequest(
            self.app.base_url + 'api/account/members-admin', 
            req_headers={"Content-Type" : "application/json",'Authorization': f'Bearer {self.app.access}'}, 
            refresh=self.app.refresh,
            on_success=self.got_members
        )
        self.get_members()
    
    def got_members(self, request:UrlRequestUrllib, result:list[dict]):
        self.members = result
        self.show_members()
    
    def show_members(self, text_filter:str=''):
        self.ids.container.clear_widgets()
        for member in self.members:
            if (any([text_filter in str(detail).lower() for detail in member.values()])):
                memberComponent = MemberComponent()
                memberComponent.set_details(member, self)
                self.ids.container.add_widget(memberComponent)
    
    def search(self, text:str, on_validate=False):
        if (not self.searched or on_validate):
            Clock.schedule_once(lambda dt:setattr(self, 'searched', False), 0.5)
            self.show_members(text)
        self.searched = True


class MemberComponent(MDCard, HoverBehavior):
    def set_details(self, member_details:dict, root:MemberScreen):
        self.root = root
        self.member_details = member_details
        self.ids.username.text = member_details.get('username')
        fullname = f"{self.member_details.get('first_name', '')} {self.member_details.get('last_name', '')}"
        email = self.member_details.get('email')
        birthdate = self.member_details.get('birthdate')
        if (fullname):
            self.ids.fullname.text = f'[b]Full Name:[/b] {fullname.strip()}'
        if (email):
            self.ids.email.text = f'[b]Email:[/b] {email}'
        if (birthdate):
            self.ids.birthdate.text = f'[b]Birthdate:[/b] {birthdate}'
    
    def on_press(self, *args):
        memberDetail = MemberDetail()
        memberDetail.set_details(self.member_details)
        self.root.ids.detail_container.clear_widgets()
        self.root.ids.detail_container.add_widget(memberDetail)
    
    def on_enter(self, *args):
        self.md_bg_color = App.get_running_app().theme['tertiary-darker']
    
    def on_leave(self, *args):
        self.md_bg_color = App.get_running_app().theme['tertiary']


class MemberDetail(MDBoxLayout):
    def set_details(self, member_details:dict):
        for key in member_details.keys():
            label = self.ids.get(key)
            detail = member_details.get(key)
            if (label and detail):
                label.text += str(detail)
        membership:dict = member_details.get('membership')
        if (membership):
            self.ids.membershipType.text += membership.get('membershipType')
            self.ids.startDate.text += membership.get('startDate')
            if (member_details.get('subscription')):
                self.ids.expirationDate.text += membership.get('expirationDate')
