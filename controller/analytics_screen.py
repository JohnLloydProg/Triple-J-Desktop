from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
from kivy.app import App
from tools import GeneralRequest
from datetime import date
import numpy as np

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
routines = {'L': 'Lower', 'C': 'Core', 'U': 'Upper', 'PS': 'Push', 'PL': 'Pull'}


class AnalyticsScreen(MDScreen):
    month:str = months[date.today().month - 1]
    peak_done = False

    def on_enter(self):
        self.app = App.get_running_app()
        self.reset_btns()
        GeneralRequest(
            self.app.base_url + 'api/analytics/members/report', 
            req_headers={"Content-Type" : "application/json",'Authorization': f'Bearer {self.app.access}'},
            on_success=self.got_members_data, refresh=self.app.refresh
        )
        self.get_activity_data()
        self.get_sales_data()
    
    def got_members_data(self, request, result):
        self.ids.pie_charts.clear_widgets()
        demographics:dict = result.get('demographics')
        memberships:dict = result.get('memberships')
        workouts:dict = result.get('workouts')
        demographics_x = []
        demographics_labels = []
        memberships_x = []
        memberships_labels = []
        workouts_x = []
        workouts_labels = []
        for key in demographics.keys():
            value = demographics[key]
            if (value > 0):
                demographics_x.append(value)
                demographics_labels.append(key)
        for key in memberships.keys():
            value = memberships[key]
            if (value > 0):
                memberships_x.append(value)
                memberships_labels.append(key)
        for key in workouts.keys():
            value = workouts[key]
            if (value > 0):
                workouts_x.append(value)
                workouts_labels.append(routines.get(key, key))

        figure, axis = plt.subplots(1, 3)
        axis[0].pie(demographics_x, labels=demographics_labels)
        axis[0].set_title('Demographics')
        axis[1].pie(memberships_x, labels=memberships_labels)
        axis[1].set_title('Memberships')
        axis[2].pie(workouts_x, labels=workouts_labels)
        axis[2].set_title('Workouts')
        self.ids.pie_charts.add_widget(FigureCanvasKivyAgg(plt.gcf()))
        plt.figure()

        self.ids.member_number.text = f'{str(result.get('number'))} Members'
    
    def get_activity_data(self):
        GeneralRequest(
            self.app.base_url + f'api/analytics/peak/{str(months.index(self.month)+1)}', 
            req_headers={"Content-Type" : "application/json",'Authorization': f'Bearer {self.app.access}'},
            on_success=self.got_activity_data, refresh=self.app.refresh
        )
    
    def got_activity_data(self, request, result):
        print(result)
        self.ids.hours_chart.clear_widgets()
        self.ids.days_chart.clear_widgets()
        hours = result.get('hours')
        days = result.get('days')

        plt.xlim(-1, 24)
        plt.ylim(0, max(hours.values()) + 1)
        plt.plot(hours.keys(), hours.values())
        plt.title('Peak Hours')
        self.ids.hours_chart.add_widget(FigureCanvasKivyAgg(plt.gcf()))
        plt.figure()
        plt.xlim(-1, 7)
        plt.ylim(0, max(days.values()) + 1)
        plt.plot(list(map(lambda day: week[int(day)], days.keys())), days.values())
        plt.title('Peak Days')
        self.ids.days_chart.add_widget(FigureCanvasKivyAgg(plt.gcf()))
        plt.figure()
    
    def get_sales_data(self):
        GeneralRequest(
            self.app.base_url + f'api/analytics/sales/{str(months.index(self.month)+1)}', 
            req_headers={"Content-Type" : "application/json",'Authorization': f'Bearer {self.app.access}'},
            on_success=self.got_sales_data, refresh=self.app.refresh
        )
    
    def got_sales_data(self, request, result):
        self.ids.sales_container.clear_widgets()
        for sale in result:
            sale_component = SalesComponent()
            sale_component.set_details(
                date=sale.get('date'),
                amount=sale.get('amount'),
                description=sale.get('description', 'N/A'),
                receipt_no=sale.get('receipt_no', 'N/A')
            )
            self.ids.sales_container.add_widget(sale_component)

    def select_month(self, month):
        self.month = month
        self.reset_btns()
        self.get_activity_data()
        self.get_sales_data()
    
    def reset_btns(self):
        for btn in self.ids.months_container.children:
            if (btn.text != self.month):
                btn.md_bg_color = self.app.theme['tertiary']
            else:
                btn.md_bg_color = self.app.theme['green']


class SalesComponent(MDBoxLayout):
    def set_details(self, date, amount, description, receipt_no):
        self.ids.date.text = date
        self.ids.amount.text = str(amount)
        self.ids.description.text = description
        self.ids.receipt_no.text = receipt_no
