from tkinter import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import string, time, os, sys, math


platform = "lin"
if any(key for key in os.environ if key.startswith('ANDROID_')) == True:
	platform = "and"

if platform == 'and':
        from usb4a import usb
        from usbserial4a import serial4a
else:
        import serial
        import serial.tools.list_ports

ser = None


pixels = int(288)
wavCoef = []
radSens = []
irrSens = []
linCoefs = []
wavelength = []
wavelengthBins = []
cieYcoefs = [0.821,568.8,46.9,40.5,    0.286,530.9,16.3,31.1]
ciey = []
unitNumber = int(0)


dataString = ""
settingsString = ""

if platform == 'and':
        usb_device_list = usb.get_usb_device_list()
        print(usb_device_list)
        device_name_list = [
                        device.getDeviceName() for device in usb_device_list
                    ]
        #serialName ='/dev/bus/usb/001/018'
        serialName = device_name_list[0]
        deviceName = usb.get_usb_device(serialName)

        while not usb.has_usb_permission(deviceName):
                usb.request_usb_permission(deviceName)
                time.sleep(1)

        ser =  serial4a.get_serial_port(serialName, 115200,8,'N',1,timeout=1)
else:
        ports = serial.tools.list_ports.comports()
        com_list = []
        for p in ports:
                com_list.append(p.device)

        print(com_list)
        #serialName = '/dev/ttyUSB0'
        serialName = com_list[0]
        ser = serial.Serial(serialName, 115200)


time.sleep(1)

root = Tk()
#root.geometry('720x1000')
root.title('OSpRad')

saveLabel = StringVar()
saveListVals = ""

interVar = IntVar()
interTime = StringVar()
interBtnRadVar = IntVar()
interBtnIrrVar = IntVar(value=1)
minNscans = StringVar()
prevMinNscans = 3
maxNscans = StringVar()
prevMaxNscans = 50;

manIntTime = StringVar()
prevManIntTime = 0

headersPrinted = 0

def getSpec(v):
    #check for change in integration time
    global prevManIntTime
    ti = int(manIntTime.get())
    if(ti != prevManIntTime):
        prevManIntTime = ti
        ts = 't' + str(ti)
        ser.write(str.encode(ts))
        print('Int time changed to ' + ts)
        #time.sleep(1)
        # wait for integration time to be updated
        output = " "
        output = ser.readline()

    #check for change in min and max n scans
    global prevMaxNscans
    global prevMinNscans
    tmin = int(minNscans.get())
    tmax = int(maxNscans.get())
    if(tmax > 50):
        tmax = 50
    if(tmin < 1):
        tmin = 1
    if(tmax < tmin):
        tmax = tmin
    if(tmin > tmax):
        tmin = tmax
    print('nScans min: ' + str(tmin) + ' max: ' + str(tmax))

    if(tmin != prevMinNscans):
            prevMinNscans = tmin
            ts = 'n' + str(tmin)
            ser.write(str.encode(ts))
            print('Min scans changed to ' + ts)
            output = " "
            output = ser.readline()

    if(tmax != prevMaxNscans):
            prevMaxNscans = tmax
            ts = 'a' + str(tmax)
            ser.write(str.encode(ts))
            print('Max scans changed to ' + ts)
            output = " "
            output = ser.readline()        
        
    ser.write(str.encode(v))
    output = " "
    while output != "":
        #output = ser.readline()
        output = ser.readline()
        if(output != b''):
            x = output.split(b',')
            #print(output)
            try:
           	 x = [float(i) for i in x]
            except:
            	settingsLabel.config(text="error reading spec")
            	print(output)
            	print("testprint")
            	file_object = open('./data.txt', 'a')
            	file_object.write("\nParse error,"+ str(output))
            	file_object.close()
            	return

            global unitNumber
            unitNumber = int(x[0])
            nScans = int(x[2])
            intTime = int(x[3])
            saturated = float(x[4])
            # clean array to only spectrum data
            x.pop(0) # [0] = unitNumber, [1] = rad/irr, [2] = nScans, [3] = integration time, [4] = saturated
            x.pop(0)
            x.pop(0)
            x.pop(0)
            x.pop(0)
            
            #------------------import calibration data from CSV---------------------
            # Script must run from same directory as calibration_data.csv
            
            global wavelength
            global wavelengthBins
            global wavCoef
            global radSens
            global irrSens
            global linCoefs
            global ciey
            if(len(wavCoef) != pixels or len(radSens) != pixels or len(irrSens) != pixels): # only load values from file the first time the code runs (to work out unit number)
                    for line in open("calibration_data.csv"):
                        row = line.split(',')
                        try:
                            int(row[0])
                        except:
                            pass
                        else:
                                if(int(row[0]) == unitNumber):
                                    if(row[1] == "wavCoef"):
                                            wavCoef = row
                                            wavCoef.pop(0)
                                            wavCoef.pop(0)
                                    if(row[1] == "radSens"):
                                            radSens = row
                                            radSens.pop(0)
                                            radSens.pop(0)
                                    if(row[1] == "irrSens"):
                                            irrSens = row
                                            irrSens.pop(0)
                                            irrSens.pop(0)
                                    if(row[1] == "linCoefs"):
                                            linCoefs = row
                                            linCoefs.pop(0)
                                            linCoefs.pop(0)
                                            

                                            
                   ##              check calibration data have loaded, if they haven't then save error
                    if(len(wavCoef) != pixels or len(radSens) != pixels or len(irrSens) != pixels or len(linCoefs) != pixels):
                        settingsLabel.config(text="error - calibration data not found\nEnsure calibration_data.csv is present\nand has data for unit #" + str(unitNumber))
                        return

                    cieySum = 0.0
                    for i in range(0,pixels):
                            wavelength.append(float(wavCoef[0])+float(wavCoef[1])*i+float(wavCoef[2])*i**2+float(wavCoef[3])*i**3+float(wavCoef[4])*i**4+float(wavCoef[5])*i**5)
                            if(wavelength[i] < cieYcoefs[1]):
                                y1 = cieYcoefs[0]*math.exp(-0.5*(wavelength[i]-cieYcoefs[1])**2/cieYcoefs[2]**2)
                            else:
                                y1 = cieYcoefs[0]*math.exp(-0.5*(wavelength[i]-cieYcoefs[1])**2/cieYcoefs[3]**2)

                            if(wavelength[i] < cieYcoefs[5]):
                                y2 = cieYcoefs[4]*math.exp(-0.5*(wavelength[i]-cieYcoefs[5])**2/cieYcoefs[6]**2)
                            else:
                                y2 = cieYcoefs[4]*math.exp(-0.5*(wavelength[i]-cieYcoefs[5])**2/cieYcoefs[7]**2)

                            ciey.append(y1 + y2)
                            cieySum += ciey[i]

                    #---set up wavelength bin widths array-------
                    for i in range(0,pixels-1):
                            wavelengthBins.append(wavelength[i+1]-wavelength[i])
                    wavelengthBins.append(wavelength[pixels-1]-wavelength[pixels-2])
                            

                    
##            print(len(wavelength))
            if len(x) != len(wavelength):
            	settingsLabel.config(text="error spec wrong length")
            	file_object = open('./data.txt', 'a')
            	file_object.write("\nLength error," + str(output))
            	file_object.close()
            	return


            lum = 0
            le = [0] * len(wavelength)
            if v == 'i':
                ts = "Irradiance W/(sqm*nm)\nInt.: "  + str(intTime)  + "ms Scans: "  + str(nScans)
                for i in range(0, len(wavelength)):
                        if float(irrSens[i]) > 0:
                                if(x[i] > 0):
                                        linMultiplier = float(linCoefs[0])*math.log((x[i]+1)*float(linCoefs[1]))
                                else:
                                        linMultiplier = -1* float(linCoefs[0])*math.log((-x[i]+1)*float(linCoefs[1]))
                                le[i] = (x[i]/linMultiplier) / (float(irrSens[i]) * intTime * wavelengthBins[i])
                                lum += le[i] * wavelengthBins[i] * ciey[i]
                lum = lum * 683
                #ts += "\nLum: " + "{:.3f}".format(lum) + "lux Sat:" + str(saturated) + "\nUnit #:" + str(unitNumber)
                if(lum > 0.1):
                        ts += "\nLum: " + f'{lum:.3f}' + "lux Sat:" + str(saturated) + "\nUnit #:" + str(unitNumber)
                else:
                        ts += "\nLum: " + f'{lum:.3e}' + "lux Sat:" + str(saturated) + "\nUnit #:" + str(unitNumber)
     
            else:
                ts = "Radiance W/(sr*sqm*nm)\nInt.: "  + str(intTime)  + "ms Scans: " +  str(nScans)
                for i in range(0, len(wavelength)):
                        if float(radSens[i]) > 0:
                                if(x[i] > 0):
                                        linMultiplier = float(linCoefs[0])*math.log((x[i]+1)*float(linCoefs[1]))
                                else:
                                        linMultiplier = -1* float(linCoefs[0])*math.log((-x[i]+1)*float(linCoefs[1]))
                                le[i] = (x[i]/linMultiplier) / (float(radSens[i]) * intTime * wavelengthBins[i])
                                lum += le[i]  * wavelengthBins[i] * ciey[i]
                lum = lum * 683
                #ts += "\nLum: " + "{:.3f}".format(lum) + "cd/sqm Sat:" + str(saturated) + "\nUnit #:" + str(unitNumber)
                if(lum > 0.1):
                        ts += "\nLum: " + f'{lum:.3f}' + "cd/sqm Sat:" + str(saturated) + "\nUnit #:" + str(unitNumber)
                else:
                        ts += "\nLum: " + f'{lum:.3e}' + "cd/sqm Sat:" + str(saturated) + "\nUnit #:" + str(unitNumber)

            
            settingsLabel.config(text=ts)
            output = ""
            global dataString
            xString =  f'{x[0]:.4f}'
            for i in range(1,pixels):
                    xString += "," + f'{x[i]:.4f}'
                    
            leString =  f'{le[0]:.4f}'
            for i in range(1,pixels):
                    leString += "," + f'{le[i]:.4e}'
                    
            if v == 'i':
                    dataString = "lux:," + f'{lum:.4e}' + ",W/(sqm*nm):," + leString + ",rawCounts:," + xString
            else:
                    dataString = "cd/sqm:," + f'{lum:.4e}' + ",W/(sr*sqm*nm):," + leString + ",rawCounts:," + xString
                    

            global settingsString
            settingsString = v +  ","  + str(intTime)  + "," +  str(nScans) +  "," +  str(saturated) +  ","
            [ax[x].clear() for x in range(1)]
            ax[0].plot(wavelength,le)
            canvas.draw()
            btSave["state"] = "normal"
            return dataString, settingsString

def saveData():
    ts = saveLabel.get()
    print("saved")
    file_object = open('./data.csv', 'a')
    
    ##-----------printer header line if it's missing---------------    
    global headersPrinted
    if headersPrinted == 0:
            global wavelength
            headerString = f'{wavelength[0]:.2f}'
            for i in range(1,pixels):
                    headerString += "," + f'{wavelength[i]:.2f}'
            headerString = "\nlabel,unit#,date,time,measurement,integrationTime,nScans,nSautrated,,,wavelength:," + headerString + ",," + headerString
            file_object.write(headerString)
            headersPrinted = 1
    
    t = time.localtime()
    ct = str(t.tm_year) + ":" + str(t.tm_mon) + ":" + str(t.tm_mday) + "," + time.strftime("%H:%M:%S", t)
    global unitNumber
    file_object.write("\n"+   ts + "," +  str(unitNumber) + "," + ct + "," +  settingsString +  dataString)
    file_object.close()
    btSave["state"] = "disabled"
    global saveListVals
    saveListVals  = ts + "\n" + saveListVals
    saveList.config(text=saveListVals)
    return saveListVals


def interFunction(tt):
        ct = time.time()
        if interVar.get() == 1:
                if ct >= tt:
                        if interBtnIrrVar.get() == 1:
                                getSpec("i")
                                saveData()
                                time.sleep(1)
                        if interBtnRadVar.get() == 1:       
                                getSpec("r")
                                saveData()
                                
                        td = int(interTime.get())
                        tt = tt + td
                root.after(1000, interFunction, tt)
			
				
def interFunction2():
	tt = time.time()
	root.after(50, interFunction, tt)


##------------LEFT-HAND FRAME-------------

left_frame = Frame(root)
left_frame.grid(row=0, column=0, sticky=N+S+E+W)
left_frame.columnconfigure(0, weight=1)
left_frame.rowconfigure(0, weight=1)
left_frame.rowconfigure(1, weight=1)
left_frame.rowconfigure(2, weight=1)
left_frame.rowconfigure(3, weight=0)
left_frame.rowconfigure(4, weight=0)
left_frame.rowconfigure(5, weight=5)

btRad = Button(left_frame, text='Radiance', command= lambda: getSpec('r'))
btRad.grid(row=0, column=0, padx=(10), pady=10, sticky=N+S+E+W)

btIrr = Button(left_frame, text='Irradiance', command=lambda: getSpec('i'))
btIrr.grid(row=1, column=0, padx=(10), pady=10, sticky=N+S+E+W)

btSave = Button(left_frame, text='Save', command=lambda: saveData(), state = "disabled")
btSave.grid(row=2, column=0, padx=(10), pady=10, sticky=N+S+E+W)

saveMessage = Label(left_frame, text = "Label")
saveMessage.grid(row=3, column=0, padx=(10), pady=10, sticky=N+S+E+W)

saveInput = Entry(left_frame, textvariable = saveLabel, width =11)
saveInput.grid(row=4, column=0, padx=(10), pady=10, sticky=N+S+E+W)

saveList = Label(left_frame, text = "Saved values:", fg="gray", justify="left")
saveList.grid(row=5, column=0, padx=(10), pady=10, sticky=N+E+W)


##------------RIGHT-HAND FRAME-------------
right_frame = Frame(root)
right_frame.grid(row=0, column=1, sticky=N+E+W)
right_frame.rowconfigure(0, weight=1)
right_frame.rowconfigure(1, weight=1)
right_frame.rowconfigure(2, weight=1)
right_frame.rowconfigure(3, weight=1)
right_frame.rowconfigure(4, weight=1)
right_frame.rowconfigure(5, weight=1)
right_frame.rowconfigure(6, weight=5)
right_frame.columnconfigure(0, weight=1)


intLabel = Label(right_frame, text = "Int. time (ms) 0=auto")
intLabel.grid(row=1, column=0, padx=(10), pady=10, sticky=N+S+W)

intInput = Entry(right_frame, textvariable = manIntTime, width =7)
intInput.grid(row=1, column=0, padx=(10), pady=10, sticky=N+S+E)
intInput.insert(END, "0")

minInput = Entry(right_frame, textvariable = minNscans, width =5)
minInput.grid(row=2, column=0, padx=(10), pady=10, sticky=N+S+W)
minInput.insert(END, "3")

nScanLabel = Label(right_frame, text = "Min and Max n scans")
nScanLabel.grid(row=2, column=0, padx=(10), pady=10, sticky=N+S)

maxInput = Entry(right_frame, textvariable = maxNscans, width =5)
maxInput.grid(row=2, column=0, padx=(10), pady=10, sticky=N+S+E)
maxInput.insert(END, "50")

interBtn = Checkbutton(right_frame, text="Repeat interval (s)", variable=interVar, command=interFunction2)
interBtn.grid(row=3, column=0, padx=(10), pady=10, sticky=N+S+W)

interTimeInput = Entry(right_frame, textvariable = interTime, width =5)
interTimeInput.grid(row=3, column=0, padx=(10), pady=10, sticky=N+S+E)
interTimeInput.insert(END, "300")

interBtnIrr = Checkbutton(right_frame, text="Repeat Irrad.", variable=interBtnIrrVar) # no command
interBtnIrr.grid(row=4, column=0, padx=(10), pady=10, sticky=N+S+W)

interBtnRad = Checkbutton(right_frame, text="Rad.", variable=interBtnRadVar) # no command
interBtnRad.grid(row=4, column=0, padx=(10), pady=10, sticky=N+S+E)

settingsLabel = Label(right_frame, text = "Settings", fg="gray", justify="left")
settingsLabel.grid(row=5, column=0, padx=(10), pady=10, sticky=N+W)


figure = plt.Figure(figsize=(5,5), facecolor='white')
canvas = FigureCanvasTkAgg(figure, right_frame)
canvas.get_tk_widget().grid(row=6, column=0, padx=(10), pady=10, sticky=N+S+E+W)
ax = [figure.add_subplot(1, 1, x+1) for x in range(1)]




root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=2)
root.rowconfigure(0, weight=1)

root.mainloop()

