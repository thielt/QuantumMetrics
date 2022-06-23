from uuid import getnode
from weakref import ref
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta, date
import pandas as pd
import numpy as np

import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import font as tkfont 

scope = [
    "https://spreadsheets.google.com/feeds",
    'https://www.googleapis.com/auth/spreadsheets',
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"]

creds_dict = []
    
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
qa = client.open('Quantum Active')
refd = qa.worksheet('REF: D')

refd_data = refd.get_all_records()
refd_df = pd.DataFrame(data = refd_data)
refd_df = refd_df[['Referring Provider', 'Attorney', 'Referral Pending']]

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


#Empty Spaces for first two columns
refd_df[['Referring Provider', 'Attorney']] = refd_df[['Referring Provider', 'Attorney']].replace(r'^\s*$', np.nan, regex=True)

#will replace every empty date with the one previous to it
where_empty = refd_df["Referral Pending"].eq('')
refd_df.loc[where_empty, 'Referral Pending'] = np.nan #pd.np.nan will be deprecated
refd_df["Referral Pending"].ffill(inplace=True)

#convert to datetime object
refd_df['Referral Pending'] = pd.to_datetime(refd_df['Referral Pending'], errors='coerce')
'''sample_date = '4/4/44'
refd_df['Referral Pending'] = pd.to_datetime(refd_df['Referral Pending'], errors='coerce').fillna(sample_date)'''
#df['Referral Pending'] = pd.to_datetime(df['Referral Pending'], format='%m/%d/%y')
#local version of time %x

#empty block
#print(providers_data[1942:1947])

refd_df['Year'] = refd_df["Referral Pending"].dt.year
refd_df['Month'] = refd_df["Referral Pending"].dt.strftime('%m/%Y') #formatting
refd_df['Quarter'] = refd_df["Referral Pending"].dt.to_period('Q')
#refd_df['Month'] = refd_df["Referral Pending"].dt.to_period('M')

#dictionary that has all dataframes of each year seperated
df_by_year = dict()
for year in refd_df['Year'].unique():
    year_data = refd_df[refd_df['Year'] == year]
    df_by_year[year] = year_data

#dictionary by month of the year
df_by_month = dict()
for month in refd_df['Month'].unique():
    month_data = refd_df[refd_df['Month'] == month]
    df_by_month[month] = month_data

refd_df['Quarter'] = refd_df['Quarter'].astype(str)
#dictionary by quarter of the year
df_by_quarter = dict()
for quarter in refd_df["Quarter"].unique():
    quarter_data = refd_df[refd_df['Quarter'] == quarter]
    df_by_quarter[quarter] = quarter_data


#second refactor
class My_GUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, Page_2):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("StartPage")

    def show_frame(self, page_name):
        #Show a frame for the given page name
        frame = self.frames[page_name]
        frame.tkraise()

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent) 
        self.controller = controller
        label = tk.Label(self, text="REF: D", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button1 = tk.Button(self, text="Metrics",
                            command=lambda: controller.show_frame("Page_2"))
        button1.pack()

class Page_2(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Choose Attorney or Provider", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        global refd_df
        tk.Label(self, text='Select option:').pack()
##
        def update_options_B(*args):
            profession = data[self.options.get()]
            self.options2.set(profession[0])
            menu = optionmenu_b['menu']
            menu.delete(0, 'end')
            for person in profession:
                menu.add_command(label=person, command=lambda nation=person: self.options2.set(nation))

        def update_options_C(*args):
            range_of_time = data2[self.options2.get()]
            self.options3.set(range_of_time[0])
            menu = optionmenu_c['menu']
            menu.delete(0, "end")
            for time_type in range_of_time:
                menu.add_command(label=time_type, command=lambda nation=time_type: self.options3.set(nation))

        data = {'Attorney': ['Yearly A', 'Quarterly A', 'Monthly A'],
                'Referring Provider': ['Yearly P', 'Quarterly P', 'Monthly P']
                }
        data2 = {'Yearly A': refd_df['Year'].unique(), 
                'Quarterly A': refd_df['Quarter'].unique(), 
                'Monthly A': refd_df['Month'].unique(), 
                'Yearly P': refd_df['Year'].unique(), 
                'Quarterly P':refd_df['Quarter'].unique(), 
                'Monthly P': refd_df['Month'].unique()
                }

        self.options = StringVar()
        self.options2 = StringVar()
        self.options3 = StringVar()

        self.options.trace('w', update_options_B)
        self.options2.trace('w', update_options_C)
        optionmenu_a = OptionMenu(self, self.options, *data.keys())
        optionmenu_b = OptionMenu(self, self.options2, '')
        optionmenu_c = OptionMenu(self, self.options3, '')

        optionmenu_a.pack()
        optionmenu_b.pack()
        optionmenu_c.pack()
        self.options.set('Attorney')
##

        tk.Button(self, text='Ok', command=self.show_option).pack()
        self.text = tk.Text(self)
        self.text.pack()
        tk.Button(self, text="Restart",
                  command=lambda: controller.show_frame("StartPage")).pack()

    def show_option(self):
        identifier = self.options.get() 
        identifier2 = self.options2.get()
        identifier3 = self.options3.get()

        self.text.delete(1.0, tk.END)   # empty widget to print new text
        
        if identifier2 == 'Yearly P' or identifier2 == 'Yearly A':
            self.text.insert(tk.END, str(df_by_year[int(identifier3[:-2])][identifier].value_counts()))
        elif identifier2 == 'Monthly P' or identifier2 == 'Monthly A':
            self.text.insert(tk.END, str(df_by_month[identifier3][identifier].value_counts()))
        elif identifier2 == 'Quarterly P' or identifier2 == 'Quarterly A':
            self.text.insert(tk.END, str(df_by_quarter[identifier3][identifier].value_counts()))
        else:
            pass
        #self.text.insert(tk.END, str(refd_df[identifier])) #needs to be string to insert

if __name__ == "__main__":
    app = My_GUI()
    app.mainloop()