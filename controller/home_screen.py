from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.pickers import MDDatePicker
from kivy.network.urlrequest import UrlRequest, UrlRequestUrllib
from kivymd.uix.behaviors import HoverBehavior
from tools import GeneralRequest
from kivy.app import App
from datetime import date
import json

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'Novermber', 'December']


def convert12h(time:str):
    if (time):
        timeIn:list[str] = time.split(':')
        timeIn_hour = int(timeIn[0])
        if 0 <= timeIn_hour <= 11 :
            period = 'AM'
            if timeIn_hour == 0:
                timeIn_hour = 12
        elif 12 <=timeIn_hour <= 23:
            period = 'PM'
            if timeIn_hour > 12:
                timeIn_hour -= 12
        time_str = f'{str(timeIn_hour)}:{timeIn[1]}:{timeIn[2]} {period}'
    else:
        time_str = 'Not Found'
    return time_str


class HomeScreen(MDScreen):
    sales_dialog:MDDialog = None
    dialog:MDDialog = None
    selected_date:date = date.today()
    year:int
    month:int
    day:int

    def on_enter(self):
        self.app = App.get_running_app()
        self.ids.date_btn.text = self.selected_date.isoformat()
        self.get_attendances = lambda: GeneralRequest(
            self.app.base_url + f"api/attendance/attendances/{str(self.selected_date.year)}/{str(self.selected_date.month)}/{str(self.selected_date.day)}",
            req_headers={"Content-Type" : "application/json",'Authorization': f'Bearer {self.app.access}'}, on_success=self.got_attendances, refresh=self.app.refresh
        )
        self.get_attendances()
    
    def got_attendances(self, request:UrlRequestUrllib, result:dict):
        self.ids.container.clear_widgets()
        for attendance in result:
            attendanceComponent = AttendanceComponent()    
            attendanceComponent.set_details(username=attendance.get('member', "Not found"), timeIn=convert12h(attendance.get('timeIn')), timeOut=convert12h(attendance.get('timeOut')), root=self)
            self.ids.container.add_widget(attendanceComponent)
    
    def open_menu(self):
        date_picker = MDDatePicker()
        date_picker.bind(on_save=self.date_selected)
        date_picker.open()


    def date_selected(self, instance, value:date, date_range):
        self.selected_date = value
        self.ids.date_btn.text = value.isoformat()
        self.get_attendances()
    
    def register_email(self, email):
        if (email):
            self.dialog = MDDialog(
                title="Email Sent",
                text="Please check your email for the verification link.",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: self.dialog.dismiss()
                    )
                ]
            )
            GeneralRequest(
                self.app.base_url + 'api/account/email-validation',
                req_body=json.dumps({'email': email}), req_headers={"Content-Type" : "application/json",'Authorization': f'Bearer {self.app.access}'},
                on_success=lambda request, result: self.dialog.open(), refresh=self.app.refresh
            )

    def call_details(self, username, timeIn, timeOut):
        GeneralRequest(
            self.app.base_url + f'api/account/member/{username}', req_headers={"Content-Type" : "application/json",'Authorization': f'Bearer {self.app.access}'},
            on_success=lambda request, result: self.display_details(username, timeIn, timeOut, result), refresh=self.app.refresh
        )
    
    def display_details(self, username, timeIn, timeOut, result:dict):
        self.ids.time_out.text = str(timeOut)
        self.ids.time_in.text = str(timeIn)
        self.ids.member_name.text = f'{result.get('first_name')} {result.get('last_name')}'
        GeneralRequest(
            self.app.base_url + f'api/account/membership?id={str(result.get('id'))}', req_headers={"Content-Type" : "application/json",'Authorization': f'Bearer {self.app.access}'}, 
            on_success=self.display_membership_expiry, refresh=self.app.refresh
        )
    
    def display_membership_expiry(self, request, result):
        self.ids.membership_type.text = result.get('membershipType')
        if (result.get('subscription')):
            self.ids.membership_expiry.text = result.get('expirationDate', 'Not Found!')
        else:
            self.ids.membership_expiry.text = ''
    
    def add_sales_record(self):
        self.sales_dialog = MDDialog(
            title="[color=EA4444]Add a Sales Record[/color]",
            type="custom",
            content_cls=SalesRecordContent(),
            md_bg_color=self.app.theme['primary'],
            auto_dismiss=False,
            buttons=[
                MDFlatButton(
                    text="Cancel",
                    theme_text_color='Custom',
                    text_color=(1, 1, 1, 1),
                    on_release=lambda x: self.sales_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Add",
                    on_release=lambda x: self.save_sales_record(),
                    md_bg_color=self.app.theme['accent'],
                )
            ]
        )
        self.sales_dialog.open()
    
    def save_sales_record(self):
        content = self.sales_dialog.content_cls
        amount = content.ids.amount
        description = content.ids.description
        receipt = content.ids.receipt
        if not amount.text:
            amount.error = True
            return
        if '.' in amount.text:
            if not all(num.isdigit() for num in amount.text.split('.')):
                amount.error = True
                return
        elif not amount.text.isdigit():
            amount.error = True
            return
        
        self.sales_dialog.buttons[1].disabled = True
        
        GeneralRequest(
            self.app.base_url + 'api/sales/add',
            req_body=json.dumps({
                'amount': float(amount.text),
                'description': description.text,
                'receipt_no': receipt.text
            }),
            req_headers={"Content-Type" : "application/json",'Authorization': f'Bearer {self.app.access}'},
            on_success=lambda request, result: self.sales_dialog.dismiss(), refresh=self.app.refresh, on_finish=self.sales_request_finish
        )
    
    def sales_request_finish(self, request):
        self.sales_dialog.buttons[1].disabled = False



class SalesRecordContent(MDBoxLayout):
    pass



class AttendanceComponent(MDBoxLayout, HoverBehavior):
    def set_details(self, username, timeIn, timeOut, root:HomeScreen):
        self.root = root
        self.username = username
        self.timeIn = timeIn
        self.timeOut = timeOut
        self.ids.username.text = username
        self.ids.timeIn.text = str(timeIn)
        self.ids.timeOut.text = str(timeOut)
        self.over = False
    
    def on_touch_up(self, instance):
        if (self.over):
            self.root.call_details(self.username, self.timeIn, self.timeOut)
    
    def on_enter(self, *args):
        self.md_bg_color = (80/255, 80/255, 80/255, 1)
        self.over = True
    
    def on_leave(self, *args):
        self.md_bg_color = (94/255, 92/255, 92/255, 1)
        self.over = False

