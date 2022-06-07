from weakref import ref
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta, date
import pandas as pd
import numpy as np

scope = [
    "https://spreadsheets.google.com/feeds",
    'https://www.googleapis.com/auth/spreadsheets',
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"]

creds_dict = {}

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
qa = client.open('Quantum Active')
refd = qa.worksheet('REF: D')
'''
Yearly
Quarterly
Monthly

Attorney Counts
Provider Counts
and how many they are referring.

Fiscal Quarters:
Q1 2022 Dates: January 1 - March 31
Q2 2022 Dates: April 1 - June 30
Q3 2022 Dates: July 1 - September 30
Q4 2022 Dates: October 1 - December 31
'''

def daterange(date1, date2): #WHOLE WEEK ARRAY
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)
today = date.today()
offset = (today.weekday() - 6) % 7
last_sunday = today - timedelta(days=offset)
whole_week= []
for dt in daterange(last_sunday, today):
    day = dt.strftime("%d")
    year = dt.strftime("%Y")
    month = dt.strftime("%m") 
    if int(month) < 10:
        month = [i for i in month]
        month = month[-1]
    if int(day) < 10:
        day = [i for i in day]
        day = day[-1]
    year = str(int(year) - 2000)
    format = month+'/'+day+'/'+year
    whole_week.append(format)

patients = refd.col_values(1)[1:]
providers = refd.col_values(4)[1:]
attornies = refd.col_values(5)[1:]
pending = refd.col_values(7)[1:]


refd_data = refd.get_all_records()
refd_df = pd.DataFrame(data = refd_data)
refd_df = refd_df[['', 'Referring Provider', 'Attorney', 'Referral Pending']]

#only replacing the empty spaces of the first three columns with NaN
refd_df[['', 'Referring Provider', 'Attorney']] = refd_df[['', 'Referring Provider', 'Attorney']].replace(r'^\s*$', np.nan, regex=True)

#will replace every empty date with the one previous to it
where_empty = refd_df["Referral Pending"].eq('')
refd_df.loc[where_empty, 'Referral Pending'] = pd.np.nan
refd_df["Referral Pending"].ffill(inplace=True)

#convert to datetime object
refd_df['Referral Pending'] = pd.to_datetime(refd_df['Referral Pending'], errors='coerce')
'''sample_date = '4/4/44'
refd_df['Referral Pending'] = pd.to_datetime(refd_df['Referral Pending'], errors='coerce').fillna(sample_date)'''

print(refd_df)

#print(providers_data[1942:1947])
#df['Referral Pending'] = pd.to_datetime(df['Referral Pending'], format='%m/%d/%y')
#local version of time %x

'''
Extrapolating consecutive columns:
print(df.loc[:,'Name': 'Pending'])
Would print all columns from Name to Pending
'''
#seperate through pandas:
#yearly - last 2 digits of pending seperated
#monthly - numbers before the first / appended to last 2 digits
#quarterly - seperated array then allocate dates/ rows


