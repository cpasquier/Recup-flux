import numpy as np
import matplotlib.pyplot as plt
import os
import tkinter as tk
import tkinter.filedialog as fd
from tkinter import Tk,StringVar,Entry
from datetime import date
from os import listdir
plt.rcParams.update({'font.size': 16, 'figure.figsize': [12.0, 6.0]})

# Get the date of the day for file naming
today = date.today()
d1 = today.strftime("%y%m%d")

# File
linedir = '.' #'/home/mar345/data/LineUp'
lfnumber = []
if os.path.isdir(linedir):
    for linefile in os.listdir(linedir):                 #scan the folder for files
        if '_lineup' in linefile:                        #get the lineup files
            lfnumber.append(linefile.split('_')[0])      #get the numbers at the end of the names of the lineup files
            lfdefault = str(max(lfnumber)+'_lineup')     #default lineup file is the last one
root = Tk()
tr_file = fd.askopenfile(parent=root, initialdir=linedir, initialfile=lfdefault, title='Select a lineup file')
root.destroy()

# Command for window closing
def close_window():
    gui.destroy()

# Screen for entering the scan numbers and x values
gui = Tk()
gui.title('Select scan numbers')
tk.Label(gui, text="Scan numbers").grid(row=0, column=0)
tk.Label(gui, text="x values").grid(row=1, column=0)
s1 = StringVar()
s2 = StringVar()
e1 = Entry(gui, textvariable=s1).grid(row=0, column=1)
e2 = Entry(gui, textvariable=s2).grid(row=1, column=1)
button1 = tk.Button(text = "OK", command = close_window).grid(row=2,pady=10)
gui.mainloop()

scan_init = s1.get()   #strings with all values together
x_init = s2.get()

scanunfold = []   #all values of scan numbers
xunfold = []      #all values of x 

scan_list1 = scan_init.split(',')   #split in a list of strings using comma separation
for i in scan_list1:
    if "-" in i:
        j = i.split('-')
        interm = np.arange(int(j[0]),int(j[-1])+1,1)  #values of scan numbers in between min-max
        for k in interm:
            scanunfold.append(k)
    else:
        scanunfold.append(int(i))

x_list1 = x_init.split(',')
for i in x_list1:
    xunfold.append(float(i))


# Scans the lineup file
searchlines = tr_file.readlines()
tr_file.close()
cntln=-1    #for counting the line we're at

with open(str(d1)+'_flux-list.dat', 'w') as f:
    f.write('Nominal x'+'\t'+'Scan'+'\t'+'Flux'+'\t'+'Date-time'+'\t'+'Dev. x'+'\n')
    for line in searchlines:
        cntln=cntln+1
        for scan_num in scanunfold:
            if ("#S "+str(scan_num)+" ") in line:   # we get the part for the right scan
                a = line.split()
                b = a[6]          #counts the number of theoretically measured points (input for ascan)
                for xvalue in xunfold:
                    dev = 1000
                    xapprox = -10
                    trapprox = -10
                    for j in np.arange(cntln+14, cntln+14+int(b)+1, 1):
                        if ("#C") in searchlines[j]:      #'#C' means the end of measurement (even if aborted)
                            break      #if there are not enough points (aborted), stops before the #C line anyway
                        else:
                            c = searchlines[j].split()
                            if abs(float(c[0])-xvalue)<dev:
                                dev = abs(float(c[0])-xvalue)
                                xapprox = c[0]
                                trapprox = c[9]

                    timeline = searchlines[cntln+1]
                    timesplit = timeline.split()
                    scantime = str(timesplit[2])+' '+str(timesplit[3])+' '+str(timesplit[4])+' '+str(timesplit[5])
                    f.write(str(xvalue)+'\t'+str(scan_num)+'\t'+str(trapprox)+'\t'+str(scantime)+'\t'+str('{:.2g}'.format(dev))+'\n')
f.close()

# Plot data
xlist = []
sc,xv,ta = np.loadtxt(str(d1)+'_flux-list.dat',usecols=(1,0,2),skiprows=1,unpack=True)
for i in np.arange(0,len(xv),1):
    if xv[i] in xlist:
        pass
    else:
        xlist.append(xv[i])
for j in xlist:
    axis1 = []
    axis2 = []
    for i in np.arange(0,len(xv),1):
        if xv[i]==j:
            axis1.append(sc[i])
            axis2.append(int(ta[i]))
    plt.plot(axis1,axis2,label='x='+str(j))
    plt.xticks(axis1)
plt.xlabel("Scan number")
plt.ylabel("Flux")
plt.legend()
plt.show()
