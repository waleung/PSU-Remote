import time
import numpy
import sys
import csv
import datetime
import os
import signal
from lib.hmp4040 import HMP4040
from lib.influx import Influx

"""---------------------------------------------------------------------------------------------------------------------------------"""
CHANNEL = 4
VOLTAGE_LIMIT = 1.7
CURRENT_START = 2.5
CURRENT_END = 0.1
CURRENT_STEPS = 0.1
TIME_IN_STEPS = 1
TIME_BETWEEN_STEPS = 1
MODE = 1 # Regular ramping: (0) / Switch on and off: (1)
INFLUX = 1 # Enable (1) or disable (0) upload to influxdb
LOCAL = 1 # Enable (1) or disable (0) saving data locally
RESOURCE_NAME = 'ASRL6::INSTR' # VISA resource name. Can be found using pyvisa.ResourceManager
MODULE_NUMBER = "20UPI7000004"
TEMPERATURE = "20C"
"""---------------------------------------------------------------------------------------------------------------------------------"""

"""Global Variables"""
hmp4040 = HMP4040(RESOURCE_NAME)

def safeExit(signum, frame):
    print("\nKeyboardInterrupt")
    hmp4040.selectChannel(CHANNEL); print("Selecting channel: " + str(CHANNEL))
    hmp4040.setChannel(False); print("Deactivating channel: " + str(CHANNEL))
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, safeExit)

    if INFLUX:
        influx = Influx()
        influx.connectInflux()
        
        if not influx.checkConnection():
            sys.exit(1)
            
    if LOCAL:
        date = datetime.datetime.now().strftime("%c")
        datename = date.replace(":", "_")
        data_file = open("data/VI_Scan_" + str(datename) + "_" + str(TEMPERATURE) + ".csv", mode = "w", newline = "")
        data_file_writer = csv.writer(data_file, delimiter = ",")
        data_file_writer.writerow(["Date: " + str(date)])
        data_file_writer.writerow(["Module_Number: " + str(MODULE_NUMBER)])
        data_file_writer.writerow(["Temperature: " + str(TEMPERATURE)])
        data_file_writer.writerow("")
        data_file_writer.writerow(["Current", "Voltage"])
        
    hmp4040.selectChannel(CHANNEL); print("Selecting channel: " + str(CHANNEL))
    hmp4040.setVoltage(VOLTAGE_LIMIT); print("Setting voltage limit to: " + str(VOLTAGE_LIMIT) + "V")
    hmp4040.setCurrent(0); print("Setting current to: " + "0" + "A")
    hmp4040.setChannel(False); print("Deactivating channel: " + str(CHANNEL))
    hmp4040.setOutput(True); print("Turning output on \n")

    current_range = numpy.arange(CURRENT_END, CURRENT_START, CURRENT_STEPS)
    current_range = numpy.append(current_range, CURRENT_START) #Add the last step
    
    for i in current_range[::-1]:
        hmp4040.setCurrent(i); print("Setting current to: " + str(i) + "A")
        if MODE:
            hmp4040.setChannel(True); print("Activating channel: " + str(CHANNEL))
        time.sleep(TIME_IN_STEPS)
        
        voltage = float(hmp4040.measureVoltage())
        time_volt_now = time.time()
        datum_voltage = [voltage, time_volt_now]
        print("Voltage: " + str(datum_voltage[0]) + "V")
        
        current = float(hmp4040.measureCurrent())
        time_curr_now = time.time()
        datum_current = [current, time_curr_now]
        print("Current: " + str(datum_current[0]) + "A")
       
        
        if MODE:
            hmp4040.setChannel(False); print("Deactivating channel: " + str(CHANNEL))
        
        if INFLUX:
            influx.writeInflux("Sensor_current", datum_current)
            influx.writeInflux("Sensor_voltage", datum_voltage)
            
        if LOCAL:
            data_file_writer.writerow([current, voltage])
            
        print("") #For readability
            
        time.sleep(TIME_BETWEEN_STEPS)
        
    if LOCAL:    
        data_file.close()
        
    hmp4040.setChannel(False); print("Deactivating channel: " + str(CHANNEL))
