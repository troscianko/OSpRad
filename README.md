# OSpRad
## An open-source, low-cost, high-sensitivity spectroradiometer

Developed by Jolyon Troscianko - 2022

Reseased under GPL-3.0 license.

This project allows users to build their own low-cost, high-sensitivity spectroradiometer for measuring radiance/irradiance based on the Hamamatsu C12880MA chip.

Testing shows that the system can measure spectral radiance down to around 0.001 cd/sqm, and irradiance down to around 0.005 lx.

Included in this project are the 3D STL files for creating your own housing, code for uploading to an arduino nano microcontroller, and a Python app for interfacing with the OSpRad spectroradiometer via desktop computer or Android smartphone (via Pydroid 3).

Code and data are released without any form of warranty, and the author accepts no liability.

## User interface app
OSpRad units are controlled through the included graphical user interface. This is written in Python 3, and can run from desktop computers (currently Linux) or Android smartphones (requires Pydroid 3 app). Simply plug in the OSpRad via USB and run this code to launch the app. The OSpRad communicates via serial connection and the USB also provides power. The app has a few dependences in Python: tkinter, matplotlib, serial, (and for Android) usb4a and usbserial4a.
![image](https://user-images.githubusercontent.com/53558556/206735364-3b1cf770-dc8e-4b96-9161-38993c282523.png)

## App running from smart phone
To run from an Android phone, install Pydroid 3, use pip to install the dependences (this requires an additional app, just follow the on-screen instructions). Then connect the phone to the OSpRad and run the code. Ensure the calibration_data.csv file is in the same directory as this python code. Most modern phones have a USB-C port, so you'll need a USB-C to USB-A (female recepticle). Which is a standard cable. Older phones with a USB-micro port require a USB-micro OTG to USB-mini cable (less common, but easy to buy online).
![image](https://user-images.githubusercontent.com/53558556/206735393-852fcddf-c2f6-4157-91d9-829ed9c3097c.png)



## Circuit Diagram:
    ![Circuit Diagram](https://user-images.githubusercontent.com/53558556/206735133-19c5051f-9946-49dd-95c0-88d3e2ee12a0.png)

## 3D printed parts:
    ![image](https://user-images.githubusercontent.com/53558556/206735271-c7213dae-bb6c-4bfd-b26a-0d071d12910c.png)

