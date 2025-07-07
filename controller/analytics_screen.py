from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivy_matplotlib_widget.uix.graph_subplot_widget import MatplotFigureSubplot
from kivy.network.urlrequest import UrlRequestUrllib
from tkinter.filedialog import asksaveasfilename
import matplotlib.pyplot as plt
from kivy.app import App
from tools import GeneralRequest
from datetime import date
from kivy_matplotlib_widget.uix.hover_widget import add_hover
from matplotlib.ticker import FormatStrFormatter
import os

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
hours12 = [
    '12AM', '1AM', '2AM', '3AM', '4AM', '5AM', '6AM', '7AM', '8AM', '9AM', '10AM', '11AM', '12PM',
    '1PM', '2PM', '3PM', '4PM', '5PM', '6PM', '7PM', '8PM', '9PM', '10PM', '11PM'
]
routines = {'L': 'Lower', 'C': 'Core', 'U': 'Upper', 'PS': 'Push', 'PL': 'Pull'}


class AnalyticsScreen(MDScreen):
    year = date.today().year
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
    
    def generate_report(self, sales_box, attendance_box, activity_box):
        GeneralRequest(
            self.app.base_url + f'api/analytics/report/{str(self.year)}/{str(months.index(self.month)+1)}?sales-report={sales_box}&attendance-report={attendance_box}&busy-activity={activity_box}',
            req_headers={"Content-Type" : "application/json",'Authorization': f'Bearer {self.app.access}'},
            on_success=self.download_file, refresh=self.app.refresh
        )
    
    def download_file(self, request:UrlRequestUrllib, result):
        print(request.resp_headers.get('content-disposition'))
        file:str = request.resp_headers.get('content-disposition')
        file = file[file.index('"')+1:file.index('.pdf')].replace('.', '-').replace(':', '-')
        name = asksaveasfilename(defaultextension='.pdf', initialdir=os.path.expanduser('~'), filetypes=[('PDF Files', '*.pdf')], initialfile=file)
        name += '.pdf' if '.pdf' not in name else ''
        with open(name, 'wb') as f:
            f.write(result)
    
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
        self.ids.pie_charts.figure = figure
        plt.figure()

        self.ids.member_number.text = f'[color=#ea4444]Active Members:[/color] [color=#ffffff]{str(result.get('number'))} Members[/color]'
    
    def get_activity_data(self):
        GeneralRequest(
            self.app.base_url + f'api/analytics/peak/{str(self.year)}/{str(months.index(self.month)+1)}', 
            req_headers={"Content-Type" : "application/json",'Authorization': f'Bearer {self.app.access}'},
            on_success=self.got_activity_data, refresh=self.app.refresh
        )
    
    def got_activity_data(self, request, result):
        print(result)
        self.ids.hours_chart.clear_widgets()
        self.ids.days_chart.clear_widgets()
        hours = result.get('hours')
        days = result.get('days')

        fig, axis = plt.subplots(1, 1)
        axis.set_xlim(-1, 24)
        axis.set_ylim(0, max(hours.values()) + 1)
        line, = axis.plot(list(map(lambda day: hours12[int(day)], hours.keys())), hours.values(), label='Hour')
        axis.set_title('Peak Hours')
        self.ids.hours_chart.figure = fig
        self.ids.hours_chart.register_lines([line])
        add_hover(self.ids.hours_chart, mode='desktop')
        plt.figure()

        fig, axis = plt.subplots(1, 1)
        axis.set_xlim(-1, 7)
        axis.set_ylim(0, max(days.values()) + 1)
        line, = axis.plot(list(map(lambda day: week[int(day)], days.keys())), days.values())
        axis.set_title('Peak Days')
        self.ids.days_chart.figure = fig
        self.ids.days_chart.register_lines([line])
        add_hover(self.ids.days_chart, mode='desktop')
        plt.figure()
    
    def get_sales_data(self):
        GeneralRequest(
            self.app.base_url + f'api/analytics/sales/{str(self.year)}/{str(months.index(self.month)+1)}', 
            req_headers={"Content-Type" : "application/json",'Authorization': f'Bearer {self.app.access}'},
            on_success=self.got_sales_data, refresh=self.app.refresh
        )
    
    def got_sales_data(self, request, result):
        self.ids.sales_container.clear_widgets()
        for sale in result:
            sale_component = SalesComponent()
            receipt_no = sale.get('receipt_no')
            description = sale.get('description')
            sale_component.set_details(
                date=sale.get('date'),
                amount=sale.get('amount'),
                description= description if (description) else 'N/A',
                receipt_no= receipt_no if (receipt_no) else 'N/A'
            )
            self.ids.sales_container.add_widget(sale_component)

    def select_month(self, month):
        if (self.month != month):
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
    
    def save_chart(self, chart:MatplotFigureSubplot):
        file = asksaveasfilename(defaultextension='.png', initialdir=os.path.expanduser('~'), filetypes=[('PNG Files', '*.png')])
        if (file):
            chart.export_to_png(file)
            print(f'Saved chart to {file}')


class SalesComponent(MDBoxLayout):
    def set_details(self, date, amount, description, receipt_no):
        self.ids.date.text = date
        self.ids.amount.text = str(amount)
        self.ids.description.text = description
        self.ids.receipt_no.text = receipt_no
