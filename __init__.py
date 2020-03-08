# -*- coding: utf-8 -*-

from multiprocessing import Process, Manager
from modules import cbpi
from modules.core.hardware import SensorPassive
from modules.core.props import Property

from bluepy import btle
from bluepy.btle import BTLEException, Scanner, DefaultDelegate

inkbird_proc = None
inkbird_manager = None
inkbird_cache = {}
inkbird_scanner = None

def calc_temp(temperature):
    temperature_bits = 16
    if temperature & (1 << (temperature_bits-1)):
        temperature -= 1 << temperature_bits
    temperature = float(temperature) / 100.0
    if cbpi.get_config_parameter("unit", "F") == "F":
        temperature = temperature * 1.8 + 32
    return temperature

def distinct(objects):
    seen = set()
    unique = []
    for obj in objects:
        if obj['uuid'] not in seen:
            unique.append(obj)
            seen.add(obj['uuid'])
    return unique

def handleDiscovery(dev):
    for (adtype, desc, value) in dev.getScanData():
        if adtype == 255:
            data = {}
            try:
                humidity = "%2.2f" % (int(value[6:8]+value[4:6], 16)/100)
                data['Humidity'] = humidity
                temperature = calc_temp(int(value[2:4]+value[:2], 16))
                temperature = "%2.2f" % (temperature)
                data['Temperature'] = temperature
                battery = int(value[14:16], 16)
                data['Battery'] = battery
            except Exception as e:
                print(e)
                pass
            return data

def init_scanner():
    scanner = Scanner()
    scanner.clear()
    scanner.start()
    return scanner

def read_inkbird(cache):
    no_results_counter = 0
    inkbird_scanner = init_scanner()
    while True:
        if not inkbird_scanner or no_results_counter >= 5:
            print("Btle went away .. restarting entire btle stack")
            inkbird_scanner = init_scanner()
        inkbird_scanner.process(timeout=8.0)
        results = inkbird_scanner.getDevices()
        for dev in results:
            new_data = handleDiscovery(dev)
            if new_data:
                inkbird_cache[dev.addr] = new_data
        if not any(results):
            no_results_counter += 1
        else:
            no_results_counter = 0
            inkbird_scanner.clear()

########
########
########
########

@cbpi.sensor
class Inkbird(SensorPassive):
    device_mac = Property.Text(
        label="Inkbird Device MAC Address",
        configurable=True,
        default_value="",
        description="MAC address of the Inkbird IBS-ITH device"
    )
    sensor_type = Property.Select("Sensor Reading Type", options=["Temperature", "Humidity"], description="Select type of reading for sensor")
    calibration_temperature = Property.Text(
        label="Inkbird Temperature Offset",
        configurable=True,
        default_value="0",
        description="This number will be added to the raw temperature reading for calibration. Negative numbers are valid."
    )
    calibration_humidity = Property.Text(
        label="Inkbird Humidity Offset",
        configurable=True,
        default_value="0",
        description="This number will be added to the raw humidity reading for calibration. Negative numbers are valid."
    )

    def init(self):
        # self.offset = offset
        print('Inkbird Init - {} - {}'.format(self.device_mac, self.sensor_type))

    def get_unit(self):
        if self.sensor_type == "Temperature":
            return "°C" if self.get_config_parameter("unit", "C") == "C" else "°F"
        elif self.sensor_type == "Humidity":
            return "%"
        else:
            return " "

    def read(self):
        if self.device_mac in inkbird_cache:
            temperature = float(inkbird_cache[self.device_mac]['Temperature']) + float(self.calibration_temperature)
            humidity = float(inkbird_cache[self.device_mac]['Humidity']) + float(self.calibration_humidity)
            print("DEBUG [{}] {}, {}, {}".format(
                self.device_mac,
                temperature,
                humidity,
                inkbird_cache[self.device_mac]['Battery']
            ))
            self.data_received(inkbird_cache[self.device_mac][self.sensor_type])

@cbpi.initalizer(order=9999)
def init(cbpi):
    global inkbird_proc
    global inkbird_manager
    global inkbird_cache
    global inkbird_scanner
    print("Inkbird initializer")

    inkbird_manager = Manager()
    inkbird_cache = inkbird_manager.dict()

    inkbird_proc = Process(name='read_inkbird', target=read_inkbird, args=(inkbird_cache,))
    inkbird_proc.daemon = True
    inkbird_proc.start()

