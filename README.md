# What it does
This project is to enable remote administration of machines through a USB serial port. You can have several machines connected to the serial router and as long as one of them is accessible over the network, you can use it to reach the other machines. This was motivated by the fact that I work remotely and also do a lot of SDN experiments that cause me to lose connectivity if something is misconfigured.

# How to build
I designed the PCB itself in KiCAD based around an Espressif Esp32-c6 chip with several CH340 USB-to-serial convertors. Everything is big enough to be hand solderable if needed, I used JLC PCB to build the PCB and assemble everything except the esp32 chip.

# Firmware Install
I use MicroPython for my firmware, it is easy to install, easy to use, and is well supported for Espressif devices. You can build from source or download the latest release from [Here](https://micropython.org/download/ESP32_GENERIC_C6/).

That download will give you a binary file that you can install to the chip using esptool.
```
pip install esptool
```
Then to push the firmware you would run the following:
```
esptool.py --port PORTNAME erase_flash
esptool.py --port PORTNAME --baud 460800 write_flash 0 FIRMWARE.bin
```
Where FIRMWARE.bin is the binary MicroPython firmware you downloaded or compiled and PORTNAME is the port when you plug the left most usb port into your computer. In my case it was /dev/ttyACM0, but it maybe /dev/ttyUSB0 or something else.

# Software Install
Now that you have the board running MicroPython, you can push the boot.py file to the board to run our serial router program. I use ampy to push files to esp chips, you can install it:
```
pip install adafruit-ampy
```
Now you can push the program which will run on boot in MicroPython
```
ampy --port /dev/ttyACM0 put boot.py /boot.py
```
Now the serial router should be running UART on the four right most usb ports and able to link between them.

# Create login shell
Now on all your machines that you want to remotely access (assuming they are running Linux):
```
sudo systemctl enable serial-getty@ttyUSB0.service
```
Replace ttyUSB0 with whatever the USB serial port shows up as.

# Access a machine
If this is running on 4 machines, you can use any 1 to access the other 3. Simple disable the login shell that is bound to the serial port:
```
sudo systemctl stop serial-getty@ttyUSB0.service
```
Next use a tool like tmux or screen to connect to the serial port
```
sudo screen /dev/ttyUSB0 9600
```
You may or may not need to specify the baud rate, I am using the default 9600 but you can also change this by modifying the boot.py and modifying the serial-getty@ttyUSB0.service.
Now that you have a screen session you can hold down the 0,1,2,3 key to connect to the login shell running bound to that specific USB port. When you are finished press ctl+d to tell the router to disconnect the ports, then close your screen session and start up your login shell again.
```
sudo systemctl start serial-getty@ttyUSB0.service
```
That's all there is to it.
