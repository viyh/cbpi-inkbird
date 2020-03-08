# [cbpi-inkbird](https://github.com/viyh/cbpi-inkbird)

Plugin for [CraftBeerPi3](http://web.craftbeerpi.com/) [[GitHub](https://github.com/Manuel83/craftbeerpi3)] that reads data from Inkbird IBS-TH1 (and IBS-TH1 Mini) temperature sensor devices via Bluetooth.

## Installation

* Clone the repo into the CBPi3 _plugins_ directory:
```
git clone https://github.com/viyh/cbpi-inkbird.git ~/craftbeerpi3/modules/plugins/Inkbird      ### CHANGE THIS TO YOUR CBPi3 DIRECTORY
```

* Install dependencies using raspbian:
```
sudo apt-get update && sudo apt-get install -y libglib2.0-dev
sudo pip install bluepy
sudo setcap 'cap_net_raw,cap_net_admin+eip' /usr/local/lib/python2.7/dist-packages/bluepy/bluepy-helper
```

* Restart CraftBeerPi3.
```
sudo /etc/init.d/craftbeerpiboot restart
```

## Usage
Install the plugin, then add Sensor hardware using the "Inkbird" type. Enter the MAC address of the Inkbird device which you can get from the Engbird mobile app. Choose whether you want to use the Temperature or the Humidity sensor value. If needed, a calibration offset value can be entered.

## Author

* [Joe Richards](https://github.com/viyh)
