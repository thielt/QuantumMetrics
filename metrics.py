#!/usr/local/bin/python
# #from weakref import ref
from itertools import count
from tkinter.tix import ROW
import gspread
import matplotlib
from matplotlib.ft2font import BOLD
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta, date
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")
import numpy as np

import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText


scope = [
    "https://spreadsheets.google.com/feeds",
    'https://www.googleapis.com/auth/spreadsheets',
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"]

creds_dict = {}

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
quantum_active = client.open('Quantum Active')
ref_a = quantum_active.worksheet("REF: A")

#INTRO
today = date.today()
offset = (today.weekday() - 6) % 7
last_sunday = today - timedelta(days=offset)
#print(f'METRICS FROM LAST SUNDAY-{last_sunday} TO TODAY-{today}: ')
line1 = f'METRICS FROM LAST SUNDAY-{last_sunday} TO TODAY-{today}: '

#Referrals
#all names
names_referrals = ref_a.col_values(1)
total_referrals = len(names_referrals)-1
#print(f'Total Current Referrals: {total_referrals}')
line2 = f'Total Current Referrals: {total_referrals}'
#DONE

#every single item as a dictionary
data_referrals = ref_a.get_all_records()

#whole week manipulation
#todays date
#current_dt = datetime.datetime.now() TEST
def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)

today = date.today()
offset = (today.weekday() - 6) % 7
#print("Offset", offset) TEST
last_sunday = today - timedelta(days=offset)
#print(last_sunday) TEST

whole_week_ref = []
for dt in daterange(last_sunday, today):
    #print(dt.strftime("%Y-%m-%d")) TEST
    day = dt.strftime("%d")
    year = dt.strftime("%Y")
    #manipulating month for spreadsheet (04 to 4)
    month = dt.strftime("%m") 
    if int(month) < 10:
        month = [i for i in month]
        month = month[-1] 
    if int(day) < 10:
        day = [i for i in day] 
        day = day[-1]

    format = month+'/'+day+'/'+year
    whole_week_ref.append(format)

#start metrics:
referral_received = ref_a.col_values(7)[1:]

#New referrals
referrals_this_week = [] #all referral dates that fall in the current week
for day in whole_week_ref:
    for cell in referral_received:
        if day == cell: #add empty date
            referrals_this_week.append(cell)
total_new_referrals = len(referrals_this_week)
#print(f'Total New Referrals this week: {total_new_referrals}')
line3 = f'Total New Referrals this week: {total_new_referrals}'
#DONE

#Status count for the week and in total
status_referrals = ref_a.col_values(6)[1:]
    #EMPTY SPACES 
if len(status_referrals) != len(referral_received):
    diff_ref = len(referral_received) - len(status_referrals)
    for empty in range(diff_ref):
        #add empty space, then make null
        status_referrals.append("Empty")
for empty in status_referrals:
    if empty == "":
        empty = "Empty" 

#0.0.2
'''Total 
Pending
Scheduled
Cancelled
Denied'''

def ref_totals(specific):
    count = 0
    for stat in status_referrals:
        if stat == specific:
            count += 1
    return count

ref_pending_total = ref_totals('Pending')
#adding empty spaces as pending
for stat_ref in status_referrals:
    if stat_ref == 'Empty':
        ref_pending_total += 1

ref_schedule_total = ref_totals('Scheduled')
ref_cancelled_total = ref_totals('Cancelled')
ref_denied_total = ref_totals('Denied')

#print(f'Total Pending: {ref_pending_total}')
line_edit_1 = f'Total Pending: {ref_pending_total}'
#print(f'Total Scheduled: {ref_schedule_total}')
line_edit_2 = f'Total Scheduled: {ref_schedule_total}'
#print(f'Total Cancelled: {ref_cancelled_total}')
line_edit_3 = f'Total Cancelled: {ref_cancelled_total}'
#print(f'Total Denied: {ref_denied_total}')
line_edit_4 = f'Total Denied: {ref_denied_total}'
#0.0.2

def status_check(which_status):
    flag_check = {}
    for index,scheduled in enumerate(status_referrals):
        if scheduled == which_status:
            flag_check[index] = True
        elif scheduled != which_status or status_referrals.value() == False: 
            flag_check[index] = False
        
    total = 0
    for index,valid_date in enumerate(referral_received):
        if flag_check[index] == True:
            if valid_date in whole_week_ref:
                total += 1
    return total

total_scheduled_referrals = status_check('Scheduled')
total_pending_referrals = status_check('Pending')
total_denied_referrals = status_check('Denied')
#total_needinfo = status_check('Need Info')

#print(f'Total Scheduled this week: {total_scheduled_referrals}')
line4 = f'Total Scheduled this week: {total_scheduled_referrals}'
#print(f'Total Pending this week: {total_pending_referrals}')
line5 = f'Total Pending this week: {total_pending_referrals}'
#print(f'Total Denied this week: {total_denied_referrals}')
line6 = f'Total Denied this week: {total_denied_referrals}'
#print(f'Total Need Info this week: {total_needinfo}') not needed
#DONE

total_cancelled_referrals = status_check('Cancelled')
#print(f'Total Canceled this week: {total_cancelled_referrals}')
line7 = f'Total Canceled this week: {total_cancelled_referrals}'

#Cancelled comments added 
comments_referrals = ref_a.col_values(14)[1:]
flag_check = {}
for index,valid_date in enumerate(referral_received):
    if valid_date in whole_week_ref:
        flag_check[index] = True
    else: 
        flag_check[index] = False

for index,stat in enumerate(status_referrals):
    if stat == 'Cancelled':
        continue
    else:
        flag_check[index] = False

#print('Cancelled Referrals Reasons:')
line8 = 'Cancelled Referrals Reasons:'

referrals_comment_list = []
line9 = []
for index, comment in enumerate(comments_referrals):
    if flag_check[index] == True:
        referrals_comment_list.append(comment)
        ##PRINT IN GUI
        line9 = referrals_comment_list

    if len(line9) == 0:
        line9.append('No cancellations in Worksheet(REF:A) were found for this week.')
#if all(value == False for value in flag_check.values()):
    #print('No cancellations in Worksheet(REF:A) were found for this week.')
    #line10 = 'No cancellations in Worksheet(REF:A) were found for this week.'
#DONE

#print(ref_a.cell(2,1).value) accesses first name on worksheet (row, col)
#alt: ref_a.acell(B1).value


####################PROCEDURES
p_a = quantum_active.worksheet("P: A")

#data = p_a.get_all_records()
'''
total procdedures all green
new procedures order date sun to saturday
number approved
number pending
number denied
number pt no want
number pt no compliant
number of attorney not compliant, metric on each attorney
graph
'''
#TOTAL PROCEDURES ALL GREEN
status_procedures = p_a.col_values(4)[1:]
order_date_procedures = p_a.col_values(12)[1:]
procedure_names = p_a.col_values(1)[1:]

total_pro = len(procedure_names) #0.0.2
#print(f'Total Procedures: {total_pro}')
line_edit_5 = f'Total Procedures: {total_pro}'

#NEW PROCEDURES (SUN TO SAT)
def daterange(date1, date2): #WHOLE WEEK ARRAY
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)
today = date.today()
offset = (today.weekday() - 6) % 7
last_sunday = today - timedelta(days=offset)
whole_week_pro = []
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
    whole_week_pro.append(format)

# New Procedures 0.0.2
new_procedures = 0
for cur_date in order_date_procedures:
    if cur_date in whole_week_pro:
        new_procedures += 1
#print(f'New Procedures: {new_procedures}')
line_edit_6 = f'New Procedures: {new_procedures}'

    #EMPTY SPACES AT END
if len(status_procedures) != len(order_date_procedures):
    diff_pro = len(order_date_procedures) - len(status_procedures)
    for empty in range(diff_pro):
        #add empty space, then make null
        status_procedures.append("Empty")
for empty in status_procedures:
    if empty == "":
        empty = "Empty" 

def status_check_pro(which_status):
    flag_check = {}
    for index,scheduled in enumerate(status_procedures):
        if scheduled == which_status:
            flag_check[index] = True
        elif scheduled != which_status or status_procedures.value() == False: 
            flag_check[index] = False
        
    total = 0
    for index,valid_date in enumerate(order_date_procedures):
        if flag_check[index] == True:
            if valid_date in whole_week_pro:
                total += 1
    return total

total_scheduled_pro = status_check_pro('Scheduled')
total_pending_pro = status_check_pro('Pending')
total_denied_pro = status_check_pro('Denied')
total_approved_pro = status_check_pro('Approved')
total_ptnowan_pro = status_check_pro('Pt No Wan')
total_ptnc_pro = status_check_pro('Pt NC')
total_attnc_pro = status_check_pro('Att NC')

#total_needinfo = status_check('Need Info')

#print(f'Total Scheduled this week: {total_scheduled_pro}')
line12 = f'Total Scheduled this week: {total_scheduled_pro}'
#print(f'Total Pending this week: {total_pending_pro}')
line13 = f'Total Pending this week: {total_pending_pro}'
#print(f'Total Denied this week: {total_denied_pro}')
line14 = f'Total Denied this week: {total_denied_pro}'
#print(f'Total Approved this week: {total_approved_pro}')
line15 = f'Total Approved this week: {total_approved_pro}'
#print(f'Total PT_NW this week: {total_ptnowan_pro}')
line15_5 = f'Total Pt No Want this week: {total_ptnowan_pro}'
#print(f'Total PT_NC this week: {total_ptnc_pro}')
line16 = f'Total PT_NC this week: {total_ptnc_pro}'
#print(f'Total ATT_NC this week: {total_attnc_pro}')
line17 = f'Total ATT_NC this week: {total_attnc_pro}'

#0.0.2 all added after line10
def pro_totals(specific):
    count = 0
    for stat in status_procedures:
        if stat == specific:
            count += 1
    return count

pro_pending_total = pro_totals('Pending')
#adding empty spaces as pending
for stat_ref in status_procedures:
    if stat_ref == 'Empty' or stat_ref =='':
        pro_pending_total += 1

pro_attnc_total = pro_totals('Att NC')
pro_approved_total = pro_totals('Approved')
pro_ptnc_total = pro_totals('Pt NC')
pro_ptnw_total = pro_totals('Pt No Want')
pro_denied_total = pro_totals('Denied')
pro_scheduled_total = pro_totals('Scheduled')

#print(f'Total Scheduled: {pro_scheduled_total}')
new11 = f'Total Scheduled: {pro_scheduled_total}'
#print(f'Total Pending: {pro_pending_total}')
line_edit_7 = f'Total Pending: {pro_pending_total}'
#print(f'Total Approved: {pro_approved_total}')
line_edit_8 = f'Total Approved: {pro_approved_total}'
#print(f'Total Denied: {pro_denied_total}')
line_edit_9 = f'Total Denied: {pro_denied_total}'
#print(f'Total PT NC: {pro_ptnc_total}')
line_edit_10 = f'Total PT NC: {pro_ptnc_total}'
#print(f'Total PT NW: {pro_ptnw_total}')
line_edit_11 = f'Total PT NW: {pro_ptnw_total}'
#print(f'Total ATT NC: {pro_attnc_total}')
line_edit_12 = f'Total ATT NC: {pro_attnc_total}'
#0.0.2


#Wanted att_nc reasons removed, remove line17_5, apl18
#ATTNC comments added 
'''comments_procedures = p_a.col_values(19)[1:]
flag_check = {}
for index,valid_date in enumerate(order_date_procedures):
    if valid_date in whole_week_pro:
        flag_check[index] = True
    else: 
        flag_check[index] = False

for index,stat in enumerate(status_procedures):
    if stat == 'Att NC':
        continue
    else:
        flag_check[index] = False
#print('Attorney Non-Compliant Procedure Reasons:')
line17_5 = 'Attorney Non-Compliant Procedure Reasons:'

attnc_comment_list_procedures = []
line18 = []
for index, comment in enumerate(comments_procedures):
    if flag_check[index] == True:
        #print(comment)
        attnc_comment_list_procedures.append(comment)
        line18 = attnc_comment_list_procedures

if len(attnc_comment_list_procedures) == 0:
    line18.append('No ATT_NC Comments in Worksheet(P:A) were found for this week.')
apl18 = line18'''
#Comments added for PT NW  
comments_procedures = p_a.col_values(19)[1:]

flag_check_pro = {}
for index,stat in enumerate(status_procedures):
    if stat == 'Pt No Want':
        flag_check_pro[index] = 0
    else:
        flag_check_pro[index] = 1

#print('PT NW Reasons:')
new17_5 = 'PT NW Reasons:'

ptnw_comment_list = []
new18 = []
for index, comment in enumerate(comments_procedures):
    if flag_check_pro[index] == 0:
        ptnw_comment_list.append(comment)

if len(ptnw_comment_list) == 0:
    ptnw_comment_list.append('No PT NW Reasons')
new18 = ptnw_comment_list

'''ptnw_box = {}
def count_occurences1(new,value):
    try:
        ptnw_box[value] = ptnw_box[value] + 1
    except KeyError as e:
        ptnw_box[value] = 1
    return 

ptnw_pro_dict = {i:v for i,v in enumerate(ptnw_comment_list)}

for spot in ptnw_comment_list:
    count_occurences1(ptnw_box, spot)'''
#0.0.2 apply to label


#Metris on each attorney
attornies_procedures = p_a.col_values(7)[1:]
d = {i:v for i,v in enumerate(attornies_procedures)}

#print('COUNTS FOR EACH ATTORNEY NON_COMPLIANT:')
line19_5 = 'COUNTS FOR EACH ATTORNEY NON_COMPLIANT:'
seen = {}
def count_occurences(new,value):
    try:
        seen[value] = seen[value] + 1
    except KeyError as e:
        seen[value] = 1
    return 
for data in attornies_procedures:
    count_occurences(seen, data)
#for counts in seen.items():
    #print(counts)
    #line20 = counts
#display dictionary in tkinter using listbox

#Attnc list 0.0.3

diff_attnc = len(procedure_names) - len(attornies_procedures)
for i in range(diff_attnc):
    attornies_procedures.append('')


def attnc_check(only_attnc):
    current_attnc = {}
    for index,scheduled in enumerate(status_procedures):
        if scheduled == only_attnc:
            current_attnc[index] = True
        elif scheduled != only_attnc or status_procedures.value() == False: 
            current_attnc[index] = False
        
    current_attnc_array = []
    for index,isNoncompliant in enumerate(attornies_procedures):
        if current_attnc[index] == True:
            current_attnc_array.append(isNoncompliant)
    return current_attnc_array
final_attnc_list = attnc_check('Att NC')



################## PNSCA
p_ns_c_a = quantum_active.worksheet("P NS/C: A")

'''
number total no shows
number new no shows for week
number remaining no shows - status = null/pending
same for cancellations
'''

names_pnsca = p_ns_c_a.col_values(1)[1:]
status_pnsca = p_ns_c_a.col_values(4)[1:]
appt_date_pnsca = p_ns_c_a.col_values(5)[1:]
cancel_reason_pnsca = p_ns_c_a.col_values(9)[1:]

#0.0.2
total_pnsca = len(names_pnsca)
#print(f'Total: {total_pnsca}')
line_edit_13 = f'Total: {total_pnsca}'

    #WHOLE WEEK ARRAY
def daterange(date1, date2): 
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)
today = date.today()
offset = (today.weekday() - 6) % 7
last_sunday = today - timedelta(days=offset)
whole_week_pnsca = []
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
    whole_week_pnsca.append(format) 
    #WHOLE WEEK ARRAY -- END

    #EMPTY SPACES CHECK
if len(status_pnsca) != len(appt_date_pnsca):
    diff_pns = len(appt_date_pnsca) - len(status_pnsca)
    for empty in range(diff_pns):
        #add empty space, then make null
        status_pnsca.append("Empty")
for empty in status_pnsca:
    if empty == "":
        empty = "Empty" 
    #EMPTY SPACES -- END 
    #Adds empty spaces at the end only

new_pnsca = 0 #0.0.2
for currentdate in appt_date_pnsca:
    if currentdate in whole_week_pnsca:
        new_pnsca += 1
#print(f'New: {new_pnsca}')
line_edit_14 = f'New: {new_pnsca}'

def status_check_pnsca(which_status):
    flag_check = {}
    for index,scheduled in enumerate(status_pnsca):
        if scheduled == which_status:
            flag_check[index] = True
        elif scheduled != which_status or status_pnsca.value() == False: 
            flag_check[index] = False
        
    total = 0
    for index,valid_date in enumerate(appt_date_pnsca):
        if flag_check[index] == True:
            if valid_date in whole_week_pnsca:
                total += 1
    return total

total_scheduled_pnsca = status_check_pnsca('scheduled')
#total_pending_pnsca = status_check('pending')
total_closed_pnsca = status_check_pnsca('closed')
total_ptnw_pnsca = status_check_pnsca('pt no want')
total_nc_pnsca = status_check_pnsca('noncompliant')

#print(f'Total Scheduled this week: {total_scheduled_pnsca}')
line23 = f'Total Scheduled this week: {total_scheduled_pnsca}'
#print(f'Total Pending this week: {total_pending_pnsca}')
#line24 = f'Total Pending this week: {total_pending_pnsca}' 
#print(f'Total Closed this week: {total_closed_pnsca}')
line25 = f'Total Closed this week: {total_closed_pnsca}'
#print(f'Total PT No Want this week: {total_ptnw_pnsca}')
line26 = f'Total PT No Want this week: {total_ptnw_pnsca}'
#print(f'Total Noncompliant this week: {total_nc_pnsca}')
line27 = f'Total Noncompliant this week: {total_nc_pnsca}' #remove line24 0.0.2

#Where status is pending or empty
remaining_pnsca = 0 #0.0.2
for curstatus in status_pnsca:
    if curstatus == '' or curstatus == 'Pending':
        remaining_pnsca += 1
#print(f'Total Remaining: {remaining_pnsca}')
line_edit_15 = f'Total Remaining: {remaining_pnsca}'


    #CANCEL REASONS
#print("CANCEL REASONS PNSCA:")
cancel_reason_pnsca_array = []
for reasons in cancel_reason_pnsca:
    cancel_reason_pnsca_array.append(reasons)
    
if len(cancel_reason_pnsca_array) == 0:
    cancel_reason_pnsca_array.append('No Cancel Reasons')

for blank in cancel_reason_pnsca_array:
    if blank == '':
        cancel_reason_pnsca_array.remove(blank)
#print(cancel_reason_pnsca_array)
line28 = cancel_reason_pnsca_array  
    #CANCEL REASONS -- END
    
#apply to label function 
#applytoLabel(cancel_reason_pnsca_array)

#################OFNSCA
ofnsc_a = quantum_active.worksheet("OF NS/C: A")

'''
number total no shows
number new no shows for week
number remaining no shows - status = null/pending

same for cancellations
'''

type_ofnsca = ofnsc_a.col_values(2)[2:]
status_ofnsca = ofnsc_a.col_values(12)[2:]
appt_date_ofnsca = ofnsc_a.col_values(5)[2:]

total_no_shows_ofnsca = 0
for t in type_ofnsca:
    if t == 'LOP No Show':
        total_no_shows_ofnsca += 1
#print(f'Total No Shows: {total_no_shows_ofnsca}')   #TOTAL NO SHOWS
line29 = f'Total No Shows: {total_no_shows_ofnsca}'

#WHOLE WEEK ARRAY
def daterange(date1, date2): 
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)
today = date.today()
offset = (today.weekday() - 6) % 7
last_sunday = today - timedelta(days=offset)
whole_week_ofnsca = []
for dt in daterange(last_sunday, today):
    day = dt.strftime("%d")
    year = dt.strftime("%Y")
    month = dt.strftime("%m") 
    if int(month) < 10:
        month = [i for i in month]
        month = month[-1]
    if int(day) < 10:
        day = [i for i in day]
        day = day [-1]
    #year = str(int(year) - 2000)
    format = month+'/'+day+'/'+year
    whole_week_ofnsca.append(format) 
#WHOLE WEEK ARRAY -- END

def status_check_ofnsca(type_script):
    flag_check = {}
    for index,t in enumerate(type_ofnsca):
        if t == type_script:
            flag_check[index] = True
        elif t != type_script or status_ofnsca.value() == False: 
            flag_check[index] = False
        
    total = 0
    for index,valid_date in enumerate(appt_date_ofnsca):
        if flag_check[index] == True:
            if valid_date in whole_week_ofnsca:
                total += 1
    return total

total_new_no_shows = status_check_ofnsca('LOP No Show')
#print(f'No Shows for the week: {total_new_no_shows}')   #NEW NO SHOWS FOR THE WEEK
line30 = f'No Shows for the week: {total_new_no_shows}'

#Remaining No Shows where null and pending
limit = total_no_shows_ofnsca + 2 #last item in no show list
no_show_status_ofnsca = ofnsc_a.col_values(12)[2:limit]
no_show_names_ofnsca = ofnsc_a.col_values(1)[2:limit]

valid_status_ofnsca = 0
for i in no_show_status_ofnsca:
    if i == 'Pending' or i == 'Scheduled' or i == 'Noncompliant' or i == "Closed" or i == "Dropped":
        valid_status_ofnsca += 1

total_remaining_no_shows = total_no_shows_ofnsca - valid_status_ofnsca
#print(f'Remaining No Shows with no status update: {total_remaining_no_shows}')
line31 = f'Remaining No Shows with no status update: {total_remaining_no_shows}'

#CANCELLATIONS
total_cancellations_ofnsca = 0
for t in type_ofnsca:
    if t == 'LOP Cancellation':
        total_cancellations_ofnsca += 1
#print(f'Total Cancellations: {total_cancellations_ofnsca}') 
line32 = f'Total Cancellations: {total_cancellations_ofnsca}'

total_new_cancellations = status_check_ofnsca('LOP Cancellation')
#print(f'Cancellations for the week: {total_new_cancellations}')
line33 = f'Cancellations for the week: {total_new_cancellations}'

#Remaining Cancellations
names_ofnsca = ofnsc_a.col_values(1)[2:]

for index, name in enumerate(names_ofnsca):
    if name == 'CANCELLATIONS':
        c_limit = index + 3

cancellation_names_ofnsca = ofnsc_a.col_values(1)[c_limit:]
cancellation_status_ofnsca = ofnsc_a.col_values(12)[c_limit:]

'''cancelled_valid_status_ofnsca = 0
for stat in cancellation_status_ofnsca:
    if stat == 'Pending' or stat == "Noncompliant" or stat == 'Scheduled' or stat == "Closed" or stat == "Dropped":
        cancelled_valid_status_ofnsca += 1

remaining_cancelled = total_cancellations_ofnsca - cancelled_valid_status_ofnsca
#print(f'Remaining Cancelled with no status update: {remaining_cancelled}')
line34 = f'Remaining Cancelled with no status update: {remaining_cancelled}'''

#new 0.0.2 remove line34
total_ofnsca = len(no_show_names_ofnsca) + len(cancellation_names_ofnsca)
#print(f'Total: {total_ofnsca}') #0.0.2
line_edit_16 = f'Total Overall: {total_ofnsca}'

new_ofnsca = 0
for newdate in appt_date_ofnsca:
    if newdate in whole_week_ofnsca:
        new_ofnsca += 1
#print(f'New: {new_ofnsca}')
line_edit_17 = f'New in worksheet: {new_ofnsca}'

diff_ofnsca = len(cancellation_names_ofnsca) - len(cancellation_status_ofnsca)
for i in range(diff_ofnsca):
    cancellation_status_ofnsca.append('')
#Empty Spaces  

remaining_ofnsca_ns = 0
for remaining in no_show_status_ofnsca:
    if remaining == 'Pending' or remaining == '':
        remaining_ofnsca_ns += 1
remaining_ofnsca_c = 0
for other_remaining in cancellation_status_ofnsca:
    if other_remaining == 'Pending' or other_remaining == '':
        remaining_ofnsca_c += 1
#print(f'Remaining No Shows: {remaining_ofnsca_ns}')
line_edit_18 = f'Remaining No Shows: {remaining_ofnsca_ns}'
#print(f'Remaining Cancellations: {remaining_ofnsca_c}')
line_edit_19 = f'Remaining Cancellations: {remaining_ofnsca_c}'

###################### MRA 
mr_a = quantum_active.worksheet("MR: A")

'''MR: A —medical records
number total
number total new inputs
number total requested weekly (mr request)
number received'''

names_mr = mr_a.col_values(1)[1:]
input_date_mr = mr_a.col_values(2)[1:]
first_request_mr = mr_a.col_values(10)[1:]
second_request_mr = mr_a.col_values(10)[1:]
final_request_mr = mr_a.col_values(10)[1:]
received_mr = mr_a.col_values(13)[1:]

    #TOTAL MR
total_mr = len(names_mr)
#print(f"Total Current Medical Records: {total_mr}")
line35 = f"Total Current Medical Records: {total_mr}"

    #WHOLE WEEK ARRAY
def daterange_mr(date1, date2): 
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)
today = date.today()
offset = (today.weekday() - 6) % 7
last_sunday = today - timedelta(days=offset)
whole_week_mr = []
for dt in daterange_mr(last_sunday, today):
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
    whole_week_mr.append(format) 
    #WHOLE WEEK ARRAY -- END

    #TOTAL NEW INPUTS
def totals(col):
    total = 0
    for date in col:
        if date in whole_week_mr:
            total += 1
    return total

total_new_mr = totals(input_date_mr)
#total_req_mr = totals(first_request_mr)
total_rec_mr = totals(received_mr)
#print(f'Total New Medical Records for the week: {total_new_mr}')
line36 = f'Total New Medical Records for the week: {total_new_mr}'
#print(f'Total Requested for the week: {total_req_mr}')
#line37 = f'Total Requested for the week: {total_req_mr}'
#print(f'Total Received for the week: {total_rec_mr}')
line38 = f'Total Received for the week: {total_rec_mr}'

# 0.0.2 remove line37
total_requests_overall = 0
for date1 in first_request_mr:
    if date1 in whole_week_mr:
        total_requests_overall += 1
for date2 in second_request_mr:
    if date2 in whole_week_mr:
        total_requests_overall += 1
for date3 in final_request_mr:
    if date3 in whole_week_mr:
        total_requests_overall += 1

#print(f'Total Requests for the week: {total_requests_overall}')
new37 = f'Total Requests for the week: {total_requests_overall}'

#PLOTS###############
'''
DESIGN:
pseudo --
wholeweek dict:
assign variables and do counts on each value
return keys/index with counts 
y axis = counts (HEIGHT)
x axis = dates
pseudo --

plt.figure(figsize=(9,6))
#plt.bar(x = df['Name'], height = df["Age"], color = 'red')
plt.bar(x = i for i in whole_week, height = pass, color = 'red')

plt.xticks(rotation = 45, fontsize = 14)
plt.yticks(fontsize = 14)
plt.title(f'Metrics for {whole_week[0]} to {whole_week[-1]}', fontsize = 16, fontweight = 'bold')
plt.xlabel('Date',fontsize = 16)
plt.ylabel('Referrals', fontsize = 16)
plt.show()

#plt.savefig(title.png) to export
#plt.savefig('sampleage_graph.jpg')

#NEED METRICS ON EACH DAY AS WELL
#whole_week[1] to whole_week[5] for i in range(1,6)
#referrals_mon
#scheduled_mon
#pending_mon
#denied_mon
#cancelled_mon

2 plots:
one for new referrals per day 
one for scheduled, pending, denied, cancelled per day
'''

def refsPerDay(day):
    refs_that_day = 0
    for cell in referral_received:
        if cell == whole_week_ref[day]:
            refs_that_day += 1
    return refs_that_day

arrRPD = []
for i in range(1,6):
    try:
        #print(f'Refs on {whole_week_ref[i]}: {refsPerDay(i)}')
        arrRPD.append(refsPerDay(i))
        arrRPD_arr = []
        arrRPD_arr.append(f'Refs on {whole_week_ref[i]}: {refsPerDay(i)}')
    except IndexError:
        pass
    continue #past current day

'''data = s1.get_all_records()
df = pd.DataFrame(data = data)'''
x = np.array(whole_week_ref[1:6])
y = np.array(arrRPD)
plt.figure(figsize=(9,6))
#plt.bar(x = df['Name'], height = df["Age"], color = 'red')
plt.bar(x,y, color = 'MidnightBlue') 

plt.xticks(rotation = 20, fontsize = 14)
plt.yticks(fontsize = 14)
plt.title(f'Referrals the week of {whole_week_ref[0]} - {whole_week_ref[-1]}', 
            fontsize = 16, 
            fontweight = 'bold')
plt.xlabel('Date',fontsize = 16)
plt.ylabel('New Referrals', fontsize = 16)
plt.savefig('ref.png')

#P:A
def ProsPerDay(day):
    pros_that_day = 0
    for cell in order_date_procedures:
        if cell == whole_week_pro[day]:
            pros_that_day += 1
    return pros_that_day

arrPPD = []
for i in range(1,6):
    '''tomorrow = date.today() + timedelta(days=1)
    t_day = tomorrow.strftime("%d")
    t_year = tomorrow.strftime("%Y")
    t_month = tomorrow.strftime("%m") 
    if int(t_month) < 10:
        t_month = [i for i in t_month]
        t_month = t_month[-1]
    t_format = t_month+'/'+t_day+'/'+t_year'''

    try:
        #print(f'Procedures on {whole_week_mr[i]}: {ProsPerDay(i)}')
        arrPPD.append(ProsPerDay(i))
    except IndexError:
        pass
    continue #past current day

'''data = s1.get_all_records()
df = pd.DataFrame(data = data)'''
x = np.array(whole_week_mr[1:6])
y = np.array(arrPPD)
plt.figure(figsize=(9,6))
#plt.bar(x = df['Name'], height = df["Age"], color = 'red')
plt.bar(x,y, color = 'Red') 

plt.xticks(rotation = 20, fontsize = 14)
plt.yticks(fontsize = 14)
plt.title(f'Procedures the week of {whole_week_pro[0]} - {whole_week_pro[-1]}', 
            fontsize = 16, 
            fontweight = 'bold')
plt.xlabel('Date',fontsize = 16)
plt.ylabel('New Procedures', fontsize = 16)
plt.savefig('pro.png')

#PNSCA
def pnsca_per_day(day):
    pns_total = 0
    for cell in appt_date_pnsca:
        if cell == whole_week_pnsca[day]:
            pns_total += 1
    return pns_total

arrPNSCA = []
for i in range(1,6):
    try:
        #print(f'PNSCA on {whole_week_pnsca[i]}: {pnsca_per_day(i)}')
        arrPNSCA.append(pnsca_per_day(i))
    except IndexError:
        pass
    continue #past current day

x = np.array(whole_week_pnsca[1:6])
y = np.array(arrPNSCA)

plt.figure(figsize=(9,6))
#plt.bar(x = df['Name'], height = df["Age"], color = 'red')
plt.bar(x,y, color = 'Aquamarine') 

plt.xticks(rotation = 20, fontsize = 14)
plt.yticks(fontsize = 14)
plt.title(f'PNSCA the week of {whole_week_pnsca[0]} - {whole_week_pnsca[-1]}', 
            fontsize = 16, 
            fontweight = 'bold')
plt.xlabel('Date',fontsize = 16)
plt.ylabel('New PNSCA appointments', fontsize = 16)
plt.savefig('pnsca.png')

#OFNSCA
def OF_per_day(day):
    ofs_that_day = 0
    for cell in appt_date_ofnsca:
        if cell == whole_week_ofnsca[day]:
            ofs_that_day += 1
    return ofs_that_day

arrOPD = []
for i in range(1,6):
    try:
        #print(f'OF on {whole_week_ofnsca[i]}: {OF_per_day(i)}')
        arrOPD.append(OF_per_day(i))
    except IndexError:
        pass
    continue #past current day

x = np.array(whole_week_ofnsca[1:6])
y = np.array(arrOPD)

plt.figure(figsize=(9,6))
#plt.bar(x = df['Name'], height = df["Age"], color = 'red')
plt.bar(x,y, color = 'Orange') 

plt.xticks(rotation = 20, fontsize = 14)
plt.yticks(fontsize = 14)
plt.title(f'OFNSCA the week of {whole_week_ofnsca[0]} - {whole_week_ofnsca[-1]}', 
            fontsize = 16, 
            fontweight = 'bold')
plt.xlabel('Date',fontsize = 16)
plt.ylabel('New OF appointments', fontsize = 16)
plt.savefig('ofnsca.png')

#MRA
def mr_per_day(day):
    mrs_that_day = 0
    for cell in input_date_mr:
        if cell == whole_week_mr[day]:
            mrs_that_day += 1
    return mrs_that_day

arrMR = []
for i in range(1,6):
    try:
        #print(f'MR inputs on {whole_week_mr[i]}: {mr_per_day(i)}')
        arrMR.append(mr_per_day(i))
    except IndexError:
        pass
    continue #past current day

x = np.array(whole_week_mr[1:6])
y = np.array(arrMR)

plt.figure(figsize=(9,6))
#plt.bar(x = df['Name'], height = df["Age"], color = 'red')
plt.bar(x,y, color = 'magenta') 

plt.xticks(rotation = 20, fontsize = 14)
plt.yticks(fontsize = 14)
plt.title(f'MR inputs the week of {whole_week_mr[0]} - {whole_week_mr[-1]}', 
            fontsize = 16, 
            fontweight = 'bold')
plt.xlabel('Date',fontsize = 16)
plt.ylabel('New MR Inputs', fontsize = 16)
plt.savefig('mra.png')



###GUI TKINTER

#function to iterate each item into GUI
def applytoLabel(current):
    n = len(current)
    element = ''
    for i in range(n):
        element = element + current[i]+'\n' 
    return element

class ScrollableNotebook(ttk.Frame):
    def __init__(self,parent,*args,**kwargs):
        ttk.Frame.__init__(self, parent, *args)
        self.xLocation = 0
        self.notebookContent = ttk.Notebook(self,**kwargs)
        self.notebookContent.pack(fill="both", expand=True)

        self.notebookTab = ttk.Notebook(self,**kwargs)
        self.notebookTab.bind("<<NotebookTabChanged>>",self._tabChanger)

        slideFrame = ttk.Frame(self)
        slideFrame.place(relx=1.0, x=0, y=1, anchor=NE)
        leftArrow = ttk.Label(slideFrame, text="\u25c0")
        leftArrow.bind("<1>",self._leftSlide)
        leftArrow.pack(side=LEFT)
        rightArrow = ttk.Label(slideFrame, text=" \u25b6")
        rightArrow.bind("<1>",self._rightSlide)
        rightArrow.pack(side=RIGHT)
        self.notebookContent.bind( "<Configure>", self._resetSlide)

    def _tabChanger(self,event):
        self.notebookContent.select(self.notebookTab.index("current"))

    def _rightSlide(self,event):
        if self.notebookTab.winfo_width()>self.notebookContent.winfo_width()-30:
            if (self.notebookContent.winfo_width()-(self.notebookTab.winfo_width()+self.notebookTab.winfo_x()))<=35:
                self.xLocation-=20
                self.notebookTab.place(x=self.xLocation,y=0)
    def _leftSlide(self,event):
        if not self.notebookTab.winfo_x()== 0:
            self.xLocation+=20
            self.notebookTab.place(x=self.xLocation,y=0)

    def _resetSlide(self,event):
        self.notebookTab.place(x=0,y=0)
        self.xLocation = 0

    def add(self,frame,**kwargs):
        if len(self.notebookTab.winfo_children())!=0:
            self.notebookContent.add(frame, text="",state="hidden")
        else:
            self.notebookContent.add(frame, text="")
        self.notebookTab.add(ttk.Frame(self.notebookTab),**kwargs)

    def forget(self,tab_id):
        self.notebookContent.forget(tab_id)
        self.notebookTab.forget(tab_id)

    def hide(self,tab_id):
        self.notebookContent.hide(tab_id)
        self.notebookTab.hide(tab_id)

    def identify(self,x, y):
        return self.notebookTab.identify(x,y)

    def index(self,tab_id):
        return self.notebookTab.index(tab_id)

    def select(self,tab_id):
        self.notebookContent.select(tab_id)
        self.notebookTab.select(tab_id)

    def tab(self,tab_id, option=None, **kwargs):
        return self.notebookTab.tab(tab_id, option=None, **kwargs)

    def tabs(self):
        return self.notebookContent.tabs()

    def enable_traversal(self):
        self.notebookContent.enable_traversal()
        self.notebookTab.enable_traversal()

class WrappingLabel(tk.Label):
    '''a type of Label that automatically adjusts the wrap to the size'''
    def __init__(self, master=None, **kwargs):
        tk.Label.__init__(self, master, **kwargs)
        self.bind('<Configure>', lambda e: self.config(wraplength=self.winfo_width()))

root=Tk()
root.title("Quantum Metrics")
notebook=ScrollableNotebook(root)
frame1=Frame(notebook)
frame2=Frame(notebook)
frame3=Frame(notebook)
frame4=Frame(notebook)
frame5=Frame(notebook)
frame6=Frame(notebook)
notebook.add(frame1,text="REF:A")
notebook.add(frame2,text="P:A")
notebook.add(frame3,text="P NS/C: A")
notebook.add(frame4,text="OF NS/C: A")
notebook.add(frame5,text="MR:A")
notebook.add(frame6,text="P:A Att NC")
notebook.pack(fill="both",expand=True)

#text=Text(frame1)
#text.pack()
#Label(frame2,text="I am Frame 2").pack()
#Label(frame3,text="I am Frame 3").pack()
#Label(frame4,text="You know i'm Frame 4").pack()

#REF:A
lab1 = Label(frame1,text=line1).pack()
spacelabel = Label(frame1, text = '').pack()
referrals_title = Label(frame1, font = BOLD, text = 'REFERRALS METRICS: ').pack()
spacelabel = Label(frame1, text = '').pack()
lab2 = Label(frame1,text=line2).pack()
lab3 = Label(frame1,text=line3).pack()
edit1 = Label(frame1,text = line_edit_1).pack()
edit2 = Label(frame1,text = line_edit_2).pack()
edit3 = Label(frame1,text = line_edit_3).pack()
edit4 = Label(frame1,text = line_edit_4).pack()
spacelabel = Label(frame1, text = '').pack()
#lab4 = Label(frame1,text=line4).pack()
#lab5 = Label(frame1,text=line5).pack()
#lab6 = Label(frame1,text=line6).pack()
#lab7 = Label(frame1,text=line7).pack()
lab8 = Label(frame1,text=line8).pack()
lab9 = WrappingLabel(frame1,text=applytoLabel(line9)).pack(expand = True, fill = tk.X)

#Procedures
procedures_title = Label(frame2, font = BOLD, text = 'PROCEDURES METRICS: ').pack()
edit5 = Label(frame2,text = line_edit_5).pack()
edit6 = Label(frame2,text = line_edit_6).pack()
new11 = Label(frame2,text=new11).pack()
edit7 = Label(frame2,text = line_edit_7).pack()
edit8 = Label(frame2,text = line_edit_8).pack()
edit9 = Label(frame2,text = line_edit_9).pack()
edit10 = Label(frame2,text = line_edit_10).pack()
edit11= Label(frame2,text = line_edit_11).pack()
edit12 = Label(frame2,text = line_edit_12).pack()
spacelabel = Label(frame2, text = '').pack()
'''lab12 = Label(frame2,text=line12).pack()
lab13 = Label(frame2,text=line13).pack()
lab14 = Label(frame2,text=line14).pack()
lab15 = Label(frame2,text=line15).pack()
lab15_5 = Label(frame2,text=line15_5).pack()
lab16 = Label(frame2,text=line16).pack()
lab17 = Label(frame2,text=line17).pack()'''

ptnw_title = Label(frame2,text = 'Pt NW Reasons:').pack()
new18 = WrappingLabel(frame2,text=applytoLabel(new18)).pack(expand = True, fill =tk.X)

#PNSCA
pnsca_title = Label(frame3, font = BOLD, text = 'P NS/C:A METRICS: ').pack()
edit13 = Label(frame3,text = line_edit_13).pack()
edit14 = Label(frame3,text = line_edit_14).pack()
edit15 = Label(frame3,text = line_edit_15).pack()
#lab20 = Label(frame3,text=line20).pack()
#lab21 = Label(frame3,text=line21).pack()
#lab22 = Label(frame3,text=line22).pack()
#lab23 = Label(frame3,text=line23).pack()
#lab24 = Label(frame3,text=line24).pack()
#lab25 = Label(frame3,text=line25).pack()
#lab26 = Label(frame3,text=line26).pack()
#lab27 = Label(frame3,text=line27).pack()
#spacelabel = Label(frame3, text = '').pack()
#line28_title = Label(frame3, text = 'CANCEL REASONS P NS/C:A: ').pack()
#lab28 = WrappingLabel(frame3,text=applytoLabel(line28)).pack(expand = True, fill = tk.X)

#OFNSCA
ofnsca_title = Label(frame4, text = 'OF NS/C:A METRICS').pack()
spacelabel = Label(frame4, text = '').pack()
#edit16 = Label(frame4,text = line_edit_16).pack()
#edit17 = Label(frame4,text = line_edit_17).pack()
#spacelabel = Label(frame4, text = '').pack()
lab29 = Label(frame4,text=line29).pack()
lab30 = Label(frame4,text=line30).pack()
edit18 = Label(frame4,text = line_edit_18).pack()
#lab31 = Label(frame4,text=line31).pack()
spacelabel = Label(frame4, text = '').pack()
lab32 = Label(frame4,text=line32).pack()
lab33 = Label(frame4,text=line33).pack()
edit19 = Label(frame4,text = line_edit_19).pack()

#MRA
mra_title = Label(frame5, text = 'MEDICAL RECORDS METRICS: ').pack()
spacelabel = Label(frame5, text = '').pack()
lab35 = Label(frame5,text=line35).pack()
lab36 = Label(frame5,text=line36).pack()
new37 = Label(frame5,text=new37).pack()
lab38 = Label(frame5,text=line38).pack()

#P:A ATTNC
lab19 = Label(frame6,text=line19_5).pack() #Counts attnc
lstbox = Listbox(frame6, width = 60) #frame2 can be root
for item in seen:
    lstbox.insert(END, '{}: {}'.format(item, seen[item]))
lstbox.pack()
spacelabel = Label(frame5, text = '').pack()
attnc_title = Label(frame6, text = 'Attornies Currently Noncompliant in P:A:').pack()
WrappingLabel(frame6, text = applytoLabel(final_attnc_list)).pack(expand = True, fill = tk.X)

Button(root, text = "Quit", command = root.destroy).pack()
root.mainloop()