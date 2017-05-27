#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt
import time
from datetime import date, datetime
import plotly.plotly as py
import plotly.graph_objs as go
import plotly

#**********************************************************
#Usage:
#$ python plotly_workrave.py 
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

#Delete columns which are no longer useful:
df=df.drop([0,'day_a','month_a','year_a','hr_a','min_a','day_d','month_d','year_d','hr_d','min_d'],axis=1)
#Remove days where arrival and departure is both at 4 am. Not sure why these exists, probably because computer has not been turned off during weekends:
df=df[df['arrival']!=df['departure']]

#########################################################################################
#Plot.ly        
#########################################################################################

fullHTML=False #If false, only div elements are produced (which can be copied into any html page)
#Remember <script src="https://cdn.plot.ly/plotly-latest.min.js"></script> in the resulting html file
#http://stackoverflow.com/questions/36262748/python-save-plotly-plot-to-local-file-and-insert-into-html

#Make the data a bit cleaner by removing outliers:
df=df[(df['arrival']<12) & (df['departure']>13)]

###****************  Hours per week ***********************************##
###****************  Mouse and keyboard movement ***********************************##

###****************  Arrival/departure scatter plot (1)  ***********************************##

trace1 = go.Scatter(
    x = df['time_a'],
    y = df['arrival'],
    mode = 'markers',
    name='Arrival'
)
trace2 = go.Scatter(
    x = df['time_a'],
    y = df['departure'],
    mode = 'markers',
    name='Departure'
)
data = [trace1, trace2]
layout = go.Layout(
    title='Scatter plot (1)',
#    xaxis=dict(
#        title='Day',
#        autotick=True,
#        titlefont=dict(
#            family='Courier New, monospace',
#            size=18,
#            color='#7f7f7f'
#        )
#    ),
    yaxis=dict(
        title='Time of day',
        autotick=False,
        dtick=1,
        titlefont=dict(
            family='Courier New, monospace',
            size=18,
            color='#7f7f7f'
        )
    )
)

fig1 = go.Figure(data=data, layout=layout)

if fullHTML:
    plotly.offline.plot(fig1, filename='arrival-departure-scatter-1.html')
else:
    arr_dep_scatter_1 = plotly.offline.plot(fig1, include_plotlyjs=False, output_type='div')
    text_file = open("arr_dep_scatter_1.txt", "w")
    text_file.write(arr_dep_scatter_1)
    text_file.close()

###****************  Arrival/departure scatter plot (2) ***********************************##

# Create a trace
trace = go.Scatter(
    x = df['arrival'],
    y = df['departure'],
    mode = 'markers',
    marker=dict(
        color='rgb(96, 96, 96)',
    ),
    name='workrave.py'
)
data = [trace]
layout = go.Layout(
    title='Scatter plot (2)',
    xaxis=dict(
        title='Arrival',
        autotick=False,
        dtick=0.5,
        titlefont=dict(
            family='Courier New, monospace',
            size=18,
            color='#7f7f7f'
        )
    ),
    yaxis=dict(
        title='Departure',
        autotick=False,
        dtick=1,
        titlefont=dict(
            family='Courier New, monospace',
            size=18,
            color='#7f7f7f'
        )
    )
)

fig2 = go.Figure(data=data, layout=layout)

if fullHTML:
    plotly.offline.plot(fig2, filename='arrival-departure-scatter-2.html')
else:
    arr_dep_scatter_2 = plotly.offline.plot(fig2, include_plotlyjs=False, output_type='div')
    text_file = open("arr_dep_scatter_2.txt", "w")
    text_file.write(arr_dep_scatter_2)
    text_file.close()

###****************  Arrival and departure boxplots ***********************************##
#(box plots created brute force style..)

#Arrival
mon = df['arrival'][df['weekday']==0]
tue = df['arrival'][df['weekday']==1]
wed = df['arrival'][df['weekday']==2]
thu = df['arrival'][df['weekday']==3]
fri = df['arrival'][df['weekday']==4]
sat = df['arrival'][df['weekday']==5]
sun = df['arrival'][df['weekday']==6]

Mon = go.Box(y=mon,name='Monday',boxmean='sd')
Tue = go.Box(y=tue,name='Tuesday',boxmean='sd')
Wed = go.Box(y=wed,name='Wednesday',boxmean='sd')
Thu = go.Box(y=thu,name='Thursday',boxmean='sd')
Fri = go.Box(y=fri,name='Friday',boxmean='sd')
Sat = go.Box(y=sat,name='Saturday',boxmean='sd')
Sun = go.Box(y=sun,name='Sunday',boxmean='sd')

data = [Mon, Tue, Wed, Thu, Fri, Sat, Sun]

layout = go.Layout(
    title='Boxplot arrival',
#    xaxis=dict(
#        title='Day',
#        autotick=False,
#        titlefont=dict(
#            family='Courier New, monospace',
#            size=18,
#            color='#7f7f7f'
#        )
#    ),
    yaxis=dict(
        title='Time of day',
        autotick=False,
        titlefont=dict(
            family='Courier New, monospace',
            size=18,
            color='#7f7f7f'
        )
    )
)

fig3 = go.Figure(data=data, layout=layout)

if fullHTML:
    plotly.offline.plot(fig3, filename='boxplot-arrival.html')
else:
    arrival_boxplot = plotly.offline.plot(fig3, include_plotlyjs=False, output_type='div')
    text_file = open("arrival_boxplot.txt", "w")
    text_file.write(arrival_boxplot)
    text_file.close()

#Departure
mon = df['departure'][df['weekday']==0]
tue = df['departure'][df['weekday']==1]
wed = df['departure'][df['weekday']==2]
thu = df['departure'][df['weekday']==3]
fri = df['departure'][df['weekday']==4]
sat = df['departure'][df['weekday']==5]
sun = df['departure'][df['weekday']==6]

Mon = go.Box(y=mon,name='Monday',boxmean='sd')
Tue = go.Box(y=tue,name='Tuesday',boxmean='sd')
Wed = go.Box(y=wed,name='Wednesday',boxmean='sd')
Thu = go.Box(y=thu,name='Thursday',boxmean='sd')
Fri = go.Box(y=fri,name='Friday',boxmean='sd')
Sat = go.Box(y=sat,name='Saturday',boxmean='sd')
Sun = go.Box(y=sun,name='Sunday',boxmean='sd')

data = [Mon, Tue, Wed, Thu, Fri, Sat, Sun]

layout = go.Layout(
    title='Boxplot departure',
#    xaxis=dict(
#        title='Day',
#        autotick=False,
#        titlefont=dict(
#            family='Courier New, monospace',
#            size=18,
#            color='#7f7f7f'
#        )
#    ),
    yaxis=dict(
        title='Time of day',
        autotick=False,
        titlefont=dict(
            family='Courier New, monospace',
            size=18,
            color='#7f7f7f'
        )
    )
)

fig4 = go.Figure(data=data, layout=layout)

if fullHTML:
    plotly.offline.plot(fig4, filename='boxplot-departure.html')
else:
    departure_boxplot = plotly.offline.plot(fig4, include_plotlyjs=False, output_type='div')
    text_file = open("departure_boxplot.txt", "w")
    text_file.write(departure_boxplot)
    text_file.close()
