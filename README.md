# workrave-stats
Python script to extract information from the workrave program.

Workrave is a program that assists in the recovery and prevention of repetitive strain injury (http://www.workrave.org/).
The program is normally set up to run in the background and give alerts on taking micro-pauses and rest breaks.
It is possible to inspect various statistics such as the number of mouse button clicks and keystrokes through the GUI.
All this information is saved in the file ~/.workrave/historystats. A file with two days of statistics may look
as follows:

```
WorkRaveStats 4
D 4 10 114 13 3 4 10 114 17 51
B 0 7 9 8 30 0 0 9 42
B 1 7 1 0 1 2 0 1 8646
B 2 7 0 0 0 0 0 0 0
m 6 11368 2821324 1691215 4392 8388 8242
D 5 10 114 9 12 5 10 114 17 20
B 0 7 2 2 45 0 0 2 0
B 1 7 0 1 0 0 0 0 12742
B 2 7 0 0 0 0 0 0 0
m 6 12742 2931484 1882849 4485 11031 8463
```

workrave.py simply scrapes this file for all relevant information and puts it into a pandas dataframe.
The most interesting information is perhaps statistics on when a user turns on and off the computer. 
This is registered since the program logs all keyboard and mouse movement. 
The script gives examples of possible visualisations using matplotlib, though more (and better) visualisations
will be added later.
