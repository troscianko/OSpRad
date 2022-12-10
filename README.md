# OSpRad
## An open-source, low-cost, high-sensitivity spectroradiometer

Developed by Jolyon Troscianko - 2022

Reseased under GPL-3.0 license.

This project allows users to build their own low-cost, high-sensitivity spectroradiometer for measuring radiance/irradiance based on the Hamamatsu C12880MA chip.

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
![image](https://user-images.githubusercontent.com/53558556/206735393-852fcddf-c2f6-4157-91d9-829ed9c3097c.png)


# Construction
## Parts list:
- Hamamatsu C12880MA chip
- 3D printed components (black PLA or ABS recommended, not PET due to IR transparency)
- Arduino Nano
- Cosine corrector: 8mm diameter, 0.5mm thick virgin PTFE sheet, sanded in circular motion with 180 grit paper
- Digital micro servo (Savox – SH-0256 recommended)
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
Use Arduino IDE to flash the firmware code to the Arduino Nano. There are four numbers in the code that you'll need to change in the supplied code (shown in comments at the top of the script). This is the ID of the unit (each unit needs its own ID so it can look up its calibration data) and the shutter wheel positions that correspond to "closed", "radiance" and "irradiance" measurement positions. Once you've flased the code to the Arduino you can make a serial connection link within Arduino IDE and send "w98" or similar to find the positions that match. Once you've found the positions, update the numbers in the Arduino code and re-flash the Arduino Nano. Now the shutter wheel will move to the correct positions.

# Calibration
Calibration data for each OSpRad unit are stored in calibration_data.csv. This includes:

## Wavelength calibration
The coefficients for the equation matching each photosite to its peak wavelength sensitivity are provided by the manufacturer when you purchase the spectrometer chip

## Linearisation data
This describes the non-linear relationship between raw photosite ADC count data and linear flux. I found this is described by the function:

c[linear] = c / ( a * ln(( c + 1 ) * b )  )

at each photosite.

## Example of linearisation model fitting with linear x-axis:
![image](https://user-images.githubusercontent.com/53558556/206866765-3232aae8-63bd-4dec-80ab-747c6e76379e.png)

## and logged x-axis to show effects at very low count numbers:
![image](https://user-images.githubusercontent.com/53558556/206866771-5d5c5ff3-211b-4721-a19d-9e68e6823c1b.png)

You can either measure this yourself for unit-specific linearisation values, or use a template, they are all very similar.


