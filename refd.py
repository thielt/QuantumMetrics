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

creds_dict = 0

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
refd_df = refd_df[['Referring Provider', 'Attorney', 'Referral Pending']]

#only replacing the empty spaces of the first three columns with NaN
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

'''
Extrapolating consecutive columns:
print(df.loc[:,'Name': 'Pending'])
Would print all columns from Name to Pending
'''
#seperate through pandas:
#yearly - last 2 digits of pending seperated
#monthly - numbers before the first / appended to last 2 digits
#quarterly - seperated array then allocate dates/ rows

#empty block
#print(providers_data[1942:1947])

'''
#using specific values to search
def getMonth(s):
    return s.split("-")[1]+"-"+s.split("-")[2] 
def getDay(s):
    return s.split("-")[0]
def getYear(s):
    return s.split("-")[0]+"-"+s.split("-")[1]
def getYearMonth(s):
    return s.split("-")[1] + "-" + s.split("-")[2]

refd_df['year'] = refd_df['Referral Pending'].apply(lambda x: getYear(x))
refd_df['month'] = refd_df['Referral Pending'].apply(lambda x: getMonth(x))
refd_df['day'] = refd_df['Referral Pending'].apply(lambda x: getDay(x))
refd_df['YearMonth'] = refd_df['Referral Pending'].apply(lambda x: getYearMonth(x))

for key, g in df.groupby(['year', 'month']):
    print(key,g)
for key, g in df.groupby(['YearMonth']):
    print key, g

#specific item
print df.groupby(['YearMonth']).get_group('Jun-13')
print df[df['YearMonth']=='Jun-13']

#specific columns and their values
print df[df['YearMonth']=='Jun-13'].abc.values
print df[df['YearMonth']=='Jun-13'].xyz.values

for x in set(df.YearMonth):
    print df[df['YearMonth']==x].abc.values
    print df[df['YearMonth']==x].xyz.values'''

'''
#unique is different values
#nunique is len unique

print(len(refd_df['Referring Provider'].unique()))
#currently 243 different providers

print(len(refd_df['Attorney'].unique()))
#currently 370 different attorneys

print(refd_df["Referring Provider"].value_counts())
#counts of every unique value'''

refd_df['Year'] = refd_df["Referral Pending"].dt.year
#refd_df['Month'] = refd_df["Referral Pending"].dt.month
refd_df['YearMonth'] = refd_df["Referral Pending"].dt.strftime('%m/%Y')
refd_df['Quarter'] = refd_df["Referral Pending"].dt.to_period('Q')
#refd_df['YearMonth'] = refd_df["Referral Pending"].dt.to_period('M')

#dictionary that has all dataframes of each year seperated
df_by_year = dict()
for year in refd_df['Year'].unique():
    year_data = refd_df[refd_df['Year'] == year]
    df_by_year[year] = year_data

#dictionary by month of the year
df_by_month = dict()
for month in refd_df['YearMonth'].unique():
    month_data = refd_df[refd_df['YearMonth'] == month]
    df_by_month[month] = month_data

df_by_quarter = dict()
for quarter in refd_df["Quarter"].unique():
    quarter_data = refd_df[refd_df['Quarter'] == quarter]
    df_by_quarter[quarter] = quarter_data

#iterate through each month
'''for month in refd_df['YearMonth'].unique():
    print(df_by_month[month])
'''

#prints individual years dataframe
#Yearly Counts 
for i in df_by_year:
    try:
        if df_by_year[i]['Attorney'].empty == False:
            print(f'Attorney Counts in year: {i}')
            print(df_by_year[i]['Attorney'].value_counts())

        if df_by_year[i]['Attorney'].empty == True:
            break
    except KeyError as e:
        break

for i in df_by_year:
    try:
        if df_by_year[i]['Referring Provider'].empty == False:
            print(f'Provider Counts in year: {i}')
            print(df_by_year[i]['Referring Provider'].value_counts())

        if df_by_year[i]['Referring Provider'].empty == True:
            break
    except KeyError as e:
        break


#Monthly Counts
for i in df_by_month:
    try:
        if df_by_month[i]['Attorney'].empty == False:
            print(f'Attorney Counts in month: {i}')
            print(df_by_month[i]['Attorney'].value_counts())

        if df_by_month[i]['Attorney'].empty == True:
            break
    except KeyError as e:
        break

for i in df_by_month:
    try:
        if df_by_month[i]['Referring Provider'].empty == False:
            print(f'Provider Counts in month: {i}')
            print(df_by_month[i]['Referring Provider'].value_counts())

        if df_by_month[i]['Referring Provider'].empty == True:
            break
    except KeyError as e:
        break


#Quarterly Counts
for i in df_by_quarter:
    try:
        if df_by_quarter[i]['Attorney'].empty == False:
            print(f'Attorney Counts in quarter: {i}')
            print(df_by_quarter[i]['Attorney'].value_counts())

        if df_by_quarter[i]['Attorney'].empty == True:
            break
    except KeyError as e:
        break

for i in df_by_quarter:
    try:
        if df_by_quarter[i]['Referring Provider'].empty == False:
            print(f'Provider Counts in quarter: {i}')
            print(df_by_quarter[i]['Referring Provider'].value_counts())

        if df_by_quarter[i]['Referring Provider'].empty == True:
            break
    except KeyError as e:
        break
