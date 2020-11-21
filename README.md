# Domoticz-KinCony-KC868-Ethernet-WiFi-Relay-Module-Plugin
Domoticz-KinCony-KC868-Ethernet-WiFi-Relay-Module-Plugin
# Support relay controller list:
KC868-H2B,H4B,H8B,H16B,H32B

KC868-H2/H2W,H4/H4W,H8/H8W,H16/H16W,H32/H32W,H32L,H32LW
![image](https://www.kincony.com/wp-content/uploads/2020/11/domoticz-32-relay.jpg)
1. Make sure you have a Raspberry Pi and installed domoticz. Here is Wiki for how to install domoticz on Raspberry_Pi

2. Download KC868 plugin file unzip and copy “KC868” folder to your PI /home/pi/domoticz/plugins
![image](https://www.kincony.com/images/domoticz/raspberry-pi-domoticz-2.png)

3. Find your KC868 Controller’s IP and Port.
![image](https://www.kincony.com/images/domoticz/ip-ethernet.jpg)
if you use ethernet port, find the Ethernet IP and Port in red box and make sure ethernet “Work Mode” is “TCP Server”.
![image](https://www.kincony.com/images/domoticz/ip-wifi.jpg)
if you use WiFi port, find the WiFi IP and Port in red box and make sure WiFi “Work Mode” is “TCP Server”.

4. Open domoticz website, goto menu “SETUP” — “HARDWARE” — Add KC868 Smart Controller.

“Type” chose “KinCony KC868 plugin”

![image](https://www.kincony.com/images/domoticz/domoticz-add-hardware-3.jpg)

Chose your KC868 Smart relay controller’s Model
![image](https://www.kincony.com/images/domoticz/domoticz-kc868-h32b-switches.png)
Now you can see 32 switches and 6 input port for sensor use. this is an example for KC868-H32B relay controller.
