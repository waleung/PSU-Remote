import time
import numpy
import sys
import csv
import datetime
import os
import signal
from lib.ki2450 import KI2450
from lib.influx import Influx

"""---------------------------------------------------------------------------------------------------------------------------------"""
CURRENT_COMPLIANCE = 0.00001
VOLTAGE_START = 0.0
VOLTAGE_END = 5
VOLTAGE_STEPS = 1
TIME_IN_STEPS = 0
TIME_BETWEEN_STEPS = 1
MODE = 0 # Regular ramping: (0) / Switch on and off: (1)
INFLUX = 1 # Enable (1) or disable (0) upload to influxdb
LOCAL = 0 # Enable (1) or disable (0) saving data locally
RESOURCE_NAME = 'USB0::0x05E6::0x2450::04424778::INSTR' # VISA resource name. Can be found using pyvisa.ResourceManager
CHIP_ID = "123ABC"
TEMPERATURE = "-10000C"
"""---------------------------------------------------------------------------------------------------------------------------------"""

if __name__ == "__main__":
    ki2450 = KI2450(RESOURCE_NAME)
    signal.signal(signal.SIGINT, ki2450.safeExit)

    if INFLUX:
        influx = Influx()
        influx.connectInflux()
        
        if not influx.checkConnection():
            sys.exit(1)
            
    if LOCAL:
        date = datetime.datetime.now().strftime("%c")
        datename = date.replace(":", "_")
        data_file = open("data/IV_Scan" + str(datename) + "_" + str(TEMPERATURE) + ".csv", mode = "w", newline = "")
        data_file_writer = csv.writer(data_file, delimiter = ",")
        data_file_writer.writerow(["Date: " + str(date)])
        data_file_writer.writerow(["CHIP_ID: " + str(CHIP_ID)])
        data_file_writer.writerow(["Temperature: " + str(TEMPERATURE)])
        data_file_writer.writerow("")
        data_file_writer.writerow(["Voltage", "Current"])
          
    ki2450.setAutoRange(True); print("Setting to autorange")
    ki2450.setSource("Voltage"); print("Setting source to voltage")
    ki2450.setCurrentCompliance(CURRENT_COMPLIANCE); print("Setting compliance to: " + str(CURRENT_COMPLIANCE))
    ki2450.setVoltage(0); print("Setting voltage to: 0.0V")
    ki2450.setOutput(True); print("Turning output on \n")

    voltage_range = numpy.arange(VOLTAGE_START, VOLTAGE_END, VOLTAGE_STEPS)
    voltage_range = numpy.append(voltage_range, VOLTAGE_END) #Add the last step
    
    for i in voltage_range:
        ki2450.setVoltage(i); print("Setting voltage to: " + str(i) + "V")
        
        time.sleep(TIME_IN_STEPS)
        
        current = float(ki2450.measureCurrent())
        time_curr_now = time.time()
        datum_current = [current, time_curr_now]
        print("Current: " + str(datum_current))
        
        voltage = float(ki2450.measureVoltage())
        time_volt_now = time.time()
        datum_voltage = [voltage, time_volt_now]
        print("Voltage: " + str(datum_voltage))
        
        if MODE:
            ki2450.setVoltage(0); print("Setting voltage to: 0.0V")
        
        if INFLUX:
            influx.writeInflux("Sensor_current", datum_current)
            influx.writeInflux("Sensor_voltage", datum_voltage)
            
        if LOCAL:
            data_file_writer.writerow([voltage, current])
            
        time.sleep(TIME_BETWEEN_STEPS)
        
    if LOCAL:    
        data_file.close()
        
    ki2450.setOutput(False); print("Turning output off")
