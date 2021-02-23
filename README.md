# KC868-H series ethernet wifi relay module: Domoticz plugin

This repository contains a Domoticz plugin for users of the  [Hangzhou Kincony Electronics KC868-H series ethernet relay modules](https://www.kincony.com/product/relay-controller).

![image](https://www.kincony.com/wp-content/uploads/2020/11/domoticz-32-relay.jpg)

The Domoticz plugin supports the following devices:
- KC868-H2
- KC868-H2B
- KC868-H2W
- KC868-H4
- KC868-H4B
- KC868-H4W
- KC868-H8
- KC868-H8B
- KC868-H8W
- KC868-H16
- KC868-H16B
- KC868-H16W
- KC868-H32
- KC868-H32B
- KC868-H32L
- KC868-H32W
- KC868-H32LW

## Installation
1. Make sure you have a Raspberry Pi and installed domoticz. Here is Wiki for how to install domoticz on Raspberry_Pi

2. Install the KC868 Domoticz plugin:
  - Create a subdirectory “KC868” in your Domotics installation's plugin directory. The default plugin directory on your Raspberry Pi is ```/home/pi/domoticz/plugins```.
![image](https://www.kincony.com/images/domoticz/raspberry-pi-domoticz-2.png)
  - Download the file "plugin.py" from this repository into your Domotics installation's plugin directory.

3. Configure your KC868 device. Find its ip address and port, and make sure "Work Mode" is set to "TCP Server".
  - when using ethernet: ![image](https://www.kincony.com/images/domoticz/ip-ethernet.jpg)
  - when using wifi: ![image](https://www.kincony.com/images/domoticz/ip-wifi.jpg) 

4. Configure the KC868 Domotics plugin for your device. Open your Domoticz installation website. Go to menu “SETUP” — “HARDWARE” — Add KC868 Smart Controller and fill out the required settings:
  -  ```Name```: Any descriptive name will do.
  -  ```Type```: Choose "KinCony KC868 plugin".
  -  ```Data Timeout```: You can leave this disabled.
  -  ```IP Address```: Your KC868’s ip address. You should be abe to find this in your dhcp server's client table.
  -  ```Port```: Your KC868's tcp server port. See above.
  -  ```Model```: Your KC868's model.
  ![image](https://www.kincony.com/images/domoticz/domoticz-add-hardware-3.jpg)

5. All set. Under switches, you should now be able to see your KC868 device's switches and inputs. Here's how it looks for the KC868-H32B with 32 relays and 6 input ports:
![image](https://www.kincony.com/images/domoticz/domoticz-kc868-h32b-switches.png)
