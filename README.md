# OSpRad
## An open-source, low-cost, high-sensitivity spectroradiometer

Developed by Jolyon Troscianko - 2022

Released under GPL-3.0 license.

This project allows users to build their own low-cost, high-sensitivity spectroradiometer for measuring radiance/irradiance based on the Hamamatsu C12880MA chip. The spectral range of ~310 to 880nm and resoltuion of ~9nm make the OSpRad particularly well suited to visual modelling.

Testing shows that the system can measure spectral radiance down to around 0.001 cd/sqm, and irradiance down to around 0.005 lx.

Included in this project are the 3D STL files for creating your own housing, code for uploading to an arduino nano microcontroller, and a Python app for interfacing with the OSpRad spectroradiometer via desktop computer or Android smartphone (via Pydroid 3).

Code and data are released without any form of warranty, and the author accepts no liability.

## User interface app
OSpRad units are controlled through the included graphical user interface. This is written in Python 3, and can run from desktop computers (currently Linux) or Android smartphones (requires Pydroid 3 app). Simply plug in the OSpRad via USB and run this code to launch the app. The OSpRad communicates via serial connection and the USB also provides power. The app has a few dependences in Python: tkinter, matplotlib, serial, (and for Android) usb4a and usbserial4a. Calibration data for the OSpRad units must be provided by placing the calibration_data.csv file (with relevant data for each specific unit#) in the same directory as you're launching the code from. Spectral data are stored in data.csv in the same directory.
![image](https://user-images.githubusercontent.com/53558556/206735364-3b1cf770-dc8e-4b96-9161-38993c282523.png)

The app saves all relevant data, including calibrated watts/(sqm * nm) or watts/(sr * sqm * nm), raw count data, integration time, number of saturated photosites (to ensure measurement isn't over-exposed), number of scans averaged, time and date of the the measurement, and a label if one was chosen.

Repeat measurements can be made by ticking the relevant checkbox (for data logging), specify whether to measure radiance, irradiance, or both, and the frequency (in seconds).

## App running from smart phone
To run from an Android phone, install Pydroid 3, use pip to install the dependences (this requires an additional app, just follow the on-screen instructions). Then connect the phone to the OSpRad and run the code. Ensure the calibration_data.csv file is in the same directory as this python code. Most modern phones have a USB-C port, so you'll need a USB-C to USB-A (female receptacle). Which is a standard cable. Older phones with a USB-micro port require a USB-micro OTG to USB-mini cable (less common, but easy to buy online).
![image](https://user-images.githubusercontent.com/53558556/207035761-f31efe3d-daf0-49bf-aa4e-54de707b840e.png)

# Construction
## Parts list:
- Hamamatsu C12880MA chip
- 3D printed components (black PLA or ABS recommended, not PET due to IR transparency)
- Arduino Nano
- Cosine corrector: 8mm diameter, 0.5mm thick virgin PTFE sheet, sanded in circular motion with 180 grit paper
- Digital micro servo (Savox ??? SH-0256 recommended)
- USB cable(s) for mobile phone. e.g. USB-C to USB-A female, and USB-A male to USB-mini
- Solder and cables (e.g. strip the cables from an old Ethernet cable, 10cm lengths)
- UV curing glue (or similar, for gluing the PTFE diffuser to the shutter wheel)
- Optional physical protection: Circular fused silica microscope cover-slip or UV-transmitting PMMA disk

The 3D printed parts will need some filing/sanding/drilling to get a snug fit between the housing and shutter wheel. File down the outside of the shutter wheel shaft to give it a smooth, circular cross-section (i.e. remove 3D printing imperfections). Then use a circular file to enlarge the hole in the housing until the two fit together snugly and the shaft rotates smoothly without play. The centre of the shutter wheel shaft might need to be enlarged slightly with a 4mm drill bit to get the screw head down inside it. To get a fit between the shutter wheel shaft and the servo, use a heat-gun or lighter flame to heat the end of the shaft, and push the two carefully together while the plastic is slightly flexible, ensuring it cools in the right angle. It will cool and harden in the correct shape, so that when screwed together it will have a nice grip.

## 3D printed parts:
![image](https://user-images.githubusercontent.com/53558556/206735271-c7213dae-bb6c-4bfd-b26a-0d071d12910c.png)


Solder the parts together as shown below. Roughly 10cm lengths of wire should be good. Note the use of different 5v sources for the servo and spectrometer chip. This is because the VIN pin suffers a voltage drop (due to its protective diode) from the USB's 5v source, which isn't quite high enough for stable spectrometer functioning.

## Circuit Diagram:
![Circuit Diagram](https://user-images.githubusercontent.com/53558556/206735133-19c5051f-9946-49dd-95c0-88d3e2ee12a0.png)

## Arduino code
Use Arduino IDE to flash the firmware code to the Arduino Nano. There are four numbers in the code that you'll need to change in the supplied code (shown in comments at the top of the script). This is the ID of the unit (each unit needs its own ID so it can look up its calibration data) and the shutter wheel positions that correspond to "closed", "radiance" and "irradiance" measurement positions. Once you've flashed the code to the Arduino you can make a serial connection link within Arduino IDE (baud rate 115200) and send "w90" to the OSpRad. This will move the servo to its central position. Now it's in this position, remove the shutter wheel from the servo and re-attach it in the nearest position to "closed" (central) as possible, to get it roughly into the correct place. Next, use the same wheel position function ("w" plus number) to work out the precise numbers associated with the three required positions. The script contains a range of examples and your numbers should be similar. Once you've found the positions, update the numbers in the Arduino code and re-flash the Arduino Nano. Now the shutter wheel will move to the correct positions.

# Calibration
Calibration data for each OSpRad unit are stored in calibration_data.csv, using tab delineation. The file takes the following format:

![image](https://user-images.githubusercontent.com/53558556/206896550-cf35ebd2-01a4-46ef-b638-2797bc92ab76.png)

The first column stores the unit#. This is the ID given to each unit (flashed to the Arduino Nano, see above). Each unit requires four rows of calibration data

This includes:

## Wavelength calibration "wavCoef"
[six coefficients required] The coefficients for the equation matching each photosite to its peak wavelength sensitivity are provided by the manufacturer when you purchase the spectrometer chip.

## Linearisation data "linCoefs"
[two coefficients] This describes the non-linear relationship between raw photosite ADC count data and linear flux. I found this is described by the function:

c[linear] = c / ( a * ln(( c + 1 ) * b )  )

at each photosite. Where c is the raw count value, and a and b are coefficients.

Example of linearisation model fitting with linear x-axis:
![image](https://user-images.githubusercontent.com/53558556/206866765-3232aae8-63bd-4dec-80ab-747c6e76379e.png)

and logged x-axis to show effects at very low count numbers:
![image](https://user-images.githubusercontent.com/53558556/206866771-5d5c5ff3-211b-4721-a19d-9e68e6823c1b.png)

You can either measure this yourself for unit-specific linearisation values, or use a template, they are all very similar.


## Spectral sensitivity calibration "radSens" and "irrSens"
[288 numbers each] This requires access to a calibrated light source (with known emission spectra). Measure that source with the OSpRad in radiance and irradiance modes. See the included calibration spreadsheet to see how spectral radiance and irradiance calibration data are created.

Alternatively, you could simply use the included data as a template, but this would cause some error as there are unit-specific spectral sensitivity differences:

## Spectral radiance sensitivity:
![image](https://user-images.githubusercontent.com/53558556/206866994-992bc599-04df-417b-9486-ac40f4764e75.png)

## Spectral irradiance sensitivity:
![image](https://user-images.githubusercontent.com/53558556/206867013-0940212b-1364-4cf7-a1a8-aa31dc41c986.png)

Note that unit "E" used a cosine corrector with a different construction, explaining its lower sensitivity.
