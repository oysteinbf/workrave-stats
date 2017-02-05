#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import date, datetime

#**********************************************************
#Usage:
#$ python workrave.py 
#The file ~/.workrave/historystats must be in the same
#folder as workrave.py
#**********************************************************

def convertTime(number):
    hr = int(number)
    m = (number-hr)*60
    hr_s = '%i' % hr
    if hr < 10:
        hr_s = '0%i' % hr
    m_s = '%i' % m
    if m < 10:
        m_s = '0%i' % m
    s = hr_s + ':' + m_s
    return s

#**********************************************************
#Prepare dataframe
#**********************************************************

df_orig = pd.read_table("historystats", skiprows=1,delim_whitespace=True,header=None) 
#Something is a bit weird with df_orig.dtypes
D = df_orig[df_orig[0]=='D']
m = df_orig[df_orig[0]=='m']

D.index = np.arange(0, len(D)) #set index to start at 0
m.index = np.arange(0, len(m))
m.rename(columns={6:'mouse',7:'key'}, inplace=True)
m.drop([0,1,2,3,4,5,8,9,10],inplace=True,axis=1)

D.loc[:,2] += 1 #Fixing the month-issue
D.loc[:,7] += 1 #Fixing the month-issue
D.loc[:,3] += 1900 #Fixing the year-issue
D.loc[:,8] += 1900 #Fixing the year-issue
df = pd.concat([D,m],axis=1)
df['arrival'] = df[4] + df[5]/60.
df['departure'] = df[9] + df[10]/60.

#Datetime--------------------------------------
#Can this be done better? It might be enough with two datetime-objects?
df.rename(columns={1:'day_a',2:'month_a',3:'year_a',4:'hr_a',5:'min_a'}, inplace=True)
df.rename(columns={6:'day_d',7:'month_d',8:'year_d',9:'hr_d',10:'min_d'}, inplace=True)
df['time_a']=df.apply(lambda x: datetime(x['year_a'],x['month_a'],x['day_a'],x['hr_a'],x['min_a'],0),axis=1)
df['time_d']=df.apply(lambda x: datetime(int(x['year_d']),int(x['month_d']),int(x['day_d']),int(x['hr_d']),int(x['min_d']),0),axis=1)
df['weekday'] = df['time_a'].apply(lambda x: x.weekday()) #Might also use isoweekday
df['week'] = df['time_a'].apply(lambda x: x.isocalendar()[1]) #Might also use isoweekday

df['length'] = df['time_d']-df['time_a'] #Timedelta
df['length']=df['length'].astype('timedelta64[s]') #convert to seconds
df['length']=df['length']/3600 #convert to hours
hoursPerWeek=df.groupby([df.year_a,df.week]).agg({'length':'sum'})

#http://stackoverflow.com/questions/24203106/pandas-group-by-calendar-week-then-plot-grouped-barplots-for-the-real-datetime

#Delete columns which are no longer useful:
df=df.drop([0,'day_a','month_a','year_a','hr_a','min_a','day_d','month_d','year_d','hr_d','min_d'],axis=1)
#Remove days where arrival and departure is both at 4 am. Not sure why these exists, probably because computer has not been turned off during weekends:
df=df[df['arrival']!=df['departure']]

#**********************************************************
#Plotting
#**********************************************************

plt.close('all')

##****************  Hours per week ***********************************##
fig1=hoursPerWeek.plot(kind='bar')#,figsize=(10,10))
fig = fig1.get_figure()
plt.grid()
plt.xlabel('week')
plt.ylabel('hours')
plt.legend().set_visible(False)
plt.tight_layout()
fig.savefig('hoursPerWeek.png')
#Might have to plot like this since it is a dataframe?!

##****************  Arrival and departure boxplots ***********************************##
labels = ('Mon','Tue','Wed','Thu','Fri','Sat','Sun')
ax1 = df.boxplot('arrival',by='weekday')
ax2 = df.boxplot('departure',by='weekday')
fig1 = ax1.get_figure()
ax1.set_xticklabels(labels)
ax1.set_ylabel('Hour')
fig2 = ax2.get_figure()
ax2.set_xticklabels(labels)
ax2.set_ylabel('Hour')
fig1.savefig('boxplot_arrival.png')
fig2.savefig('boxplot_leave.png')

##Arrival and leave can also be combined in one plot:
#bp_arrival_leave = df.boxplot(column=['arrival','departure'],by='weekday')

##****************  Other plots ***********************************##
#Comment: Using pandas plotting might be easier

width = 0.4
xlocs = np.arange(len(df))

fig, ax = plt.subplots()
df['key'].plot(kind='bar',title='Keyboard usage')
fig.savefig('usage.png')

fig2, ax = plt.subplots()
ax.plot(df['arrival'], 'b^', label='Arrival')
ax.plot(df['departure'], 'go', label='Departure')
#ax.legend(loc='best')
ax.set_xlabel('Day')
ax.set_ylabel('Hour')
ax.grid(axis='y')
#plt.yticks(np.arange(6, 24, 1.0))
plt.yticks(np.arange(np.floor(df['arrival'].min()), np.ceil(df['departure'].max())+1, 1.0))
plt.title('Arrival and departure')
fig2.savefig('duration.png')

fig3, ax = plt.subplots()
ax.bar(xlocs,df['length'],width, label='Length')
ax.set_xlabel('Day')
ax.set_ylabel('Hours')
ax.grid(axis='y')
plt.yticks(np.arange(1, 15, 1.0))
fig3.savefig('length.png')

fig4, ax = plt.subplots()
a = df.sort(columns='length',ascending=False)
ax.bar(xlocs,a['length'],width, label='Length')
ax.set_xlabel('Day')
ax.set_ylabel('Hours')
ax.grid(axis='y')
plt.yticks(np.arange(1, 15, 1.0))
fig4.savefig('length_sorted.png')

#**********************************************************
#Old code
#**********************************************************
#arrival = np.zeros(7)
#departure = np.zeros(7)
#mean_length = np.zeros(7)
#
#Mon_arrival = np.array(df['arrival'][df['weekday']==0])
#Tue_arrival = np.array(df['arrival'][df['weekday']==1])
#Wed_arrival = np.array(df['arrival'][df['weekday']==2])
#Thu_arrival = np.array(df['arrival'][df['weekday']==3])
#Fri_arrival = np.array(df['arrival'][df['weekday']==4])
#Sat_arrival = np.array(df['arrival'][df['weekday']==5])
#Sun_arrival = np.array(df['arrival'][df['weekday']==6])
#
#Mon_departure = np.array(df['departure'][df['weekday']==0])
#Tue_departure = np.array(df['departure'][df['weekday']==1])
#Wed_departure = np.array(df['departure'][df['weekday']==2])
#Thu_departure = np.array(df['departure'][df['weekday']==3])
#Fri_departure = np.array(df['departure'][df['weekday']==4])
#Sat_departure = np.array(df['departure'][df['weekday']==5])
#Sun_departure = np.array(df['departure'][df['weekday']==6])
#
#boxplot_Arrival = [Mon_arrival,Tue_arrival,Wed_arrival,Thu_arrival,
#                   Fri_arrival,Sat_arrival,Sun_arrival]
#
#boxplot_Departure = [Mon_departure,Tue_departure,Wed_departure,Thu_departure,
#                   Fri_departure,Sat_departure,Sun_departure]
#
#f, (ax1, ax2) = plt.subplots(1,2,figsize=(14, 7))
#labels = ('Mon','Tue','Wed','Thu','Fri','Sat','Sun')
#
#ax1.boxplot(boxplot_Arrival)
#ax1.set_xticklabels(labels)
#ax1.set_ylabel('Hour')
#ax1.set_title('Arrival')
#ax1.grid(axis='y')
##ax2.set_yticks(np.arange(7,12,1.0))
#
#ax2.boxplot(boxplot_Departure)
#ax2.set_xticklabels(labels)
##ax2.set_ylabel('Time')
#ax2.set_title('Departure')
#ax2.grid(axis='y')
#ax2.set_yticks(np.arange(12,24,1.0))
#
#f.savefig('boxplot.png')

#date_arrival = np.array([date(df.loc[i,3],df.loc[i,2],df.loc[i,1]) for i in xrange(len(df['arrival']))])
