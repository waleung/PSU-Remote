import sys
import getopt
import time
import textwrap
import multiprocessing.connection
import multiprocessing
import os
import json
import os.path
from lib.hmp4040 import HMP4040
from lib.influx import Influx

def tcpConnection(queue):
    if os.name == "nt":
        connection_type = "Windows Named Pipe"
        listener = multiprocessing.connection.Listener(address = r"\\.\pipe" + "\hmp4040", family = "AF_PIPE")
    elif os.name == "posix":
        connection_type = "Unix Domain Socket"
        listener = multiprocessing.connection.Listener(address = ".\hmp4040", family = "AF_UNIX")
    while True:
        conn = listener.accept()
        print(connection_type + " Connected!")
        while True:
            try:
                data_available = conn.poll()
            except:
                print("Cannot receive data, aborting connection")
                break
            
            if data_available:
                try:
                    msg = conn.recv()
                except:
                    print("No data to receive, aborting connection")
                    break
                queue.put_nowait(msg)
                break
    #listener.close()

def doInterlock(psu, channel):
    print("\33[30;101m" + "Interlock has been activated" + "\33[0m")
    print("\33[30;101m" + "Setting Output to Channel " + str(channel) + " off" + "\33[0m")
    psu.selectChannel(channel)
    psu.setChannel(False)

def limit(value, output):
    if (value > 2.0) and (output == 'voltage'):
        print("\33[30;103m" + "Warning: Voltage limit must be set to 2.0V or under" + "\33[0m")
        return False
    elif (value > 4.5) and (output == 'current'):
        print("\33[30;103m" + "Current limit must be set to 4.0A or under" + "\33[0m")
        return False
    else:
        return True

def usage():
    print('\nUsage: <hmp4040_remote.py> -c channel | -s/i/v/a/o argument | -m/d | -h help')
    
def help():
    helpMessage = """
        options:
        -h, --help      show this help message and exit
        -c --channel    select channel (1-4)
        -s --setting    set the system to Local (0), Mixed (1) or Remote (2) mode. Example: -s 1
        -i --current    set the current on selected channel
        -v --voltage    set the voltage on selected channel
        -a --activate   activate (1) or deactivate (0) the selected channel
        -o --output     set the general ouput to on (1) or off (0): 
        -d --display    shows the display on the psu
        -m --monitor    starts the monitoring of voltage and current and uploads them to influx db. 
                        The influxdb settings must be configured in the influxdb.json file """

    print(textwrap.dedent(helpMessage))
    
def getJsonConfig():
    with open(os.path.dirname(__file__) + "./configs/hmp4040.json") as file:
        return json.load(file)

def main(argv):
    jsonConfigs = getJsonConfig()
    resource_name = jsonConfigs.get("resource_name")
    hmp4040 = HMP4040(resource_name)
    display = False
    monitor = False
    channel = 0
    
    argv = argv[1:]
    
    try:
        opts, args = getopt.getopt(argv, "s:c:i:v:a:o:mdh", ["setting=", "channel=" ,"current=", "voltage=", "activate=","output=", "display", "monitor", "help"])
    except Exception as e:
        print(e)
        usage()
        help()
        sys.exit(2)
        
    for opt, arg in opts:
        if opt in ("-c", "--channel"):
            channel = arg
            hmp4040.selectChannel(channel)
            print("Selecting channel: " + arg)
                 
        elif opt in ("-v", "--voltage"):
            if limit(float(arg), 'voltage'):
                hmp4040.setVoltage(arg)
                print("Setting voltage to: " + arg + "V")
            
        elif opt in ("-i", "--current"):
            if limit(float(arg), 'current'):
                hmp4040.setCurrent(arg)
                print("Setting current to: " + arg + "A")
            
        elif opt in ("-a", "--activate"):
            state = True if arg == "1" else False
            print("Activate channel: " + str(state))
            hmp4040.setChannel(arg)
            
        elif opt in ("-o", "--output"):
            state = True if arg == "1" else False
            print("Output: " + str(state))
            hmp4040.setOutput(arg)
        
        elif opt in ("-s", "--setting"):
            if arg == "0":
                hmp4040.enableSystemLocal()
            elif arg == "1":
                hmp4040.enableSystemMix()
            elif arg == "2":
                hmp4040.enableSystemRemote()
                
        elif opt in ("-d", "--display"):
            display = True
            
        elif opt in ("-m", "--monitor"):
            monitor = True
            
        elif opt in ("-h", "--help"):
            help()
            sys.exit(0)
            
        #Handle potential errors    
        if hmp4040.error:
            print("\33[30;101m" + "Error: " + hmp4040.errorMessage[0:-1] + " Command: " + hmp4040.command[0:-1] + "\33[0m")
            sys.exit(1)
           
    if display:
        printMessage = ""
        
        output = True if int(hmp4040.displayOutput()) else False
    
        for i in range(1, 4 + 1):
            hmp4040.selectChannel(i)
            
            active = True if int(hmp4040.displayActiveChannel()) else False
            
            if active and output:
                printMessage += f"Channel: {hmp4040.displayChannel()[0:-1]} V: {hmp4040.measureVoltage()[0:-1]}V I: {hmp4040.measureCurrent()[0:-1]}A Active: {active}\n"
            else:
                printMessage += f"Channel: {hmp4040.displayChannel()[0:-1]} V: {hmp4040.displayVoltage()[0:-1]}V I: {hmp4040.displayCurrent()[0:-1]}A Active: {active}\n"
                
        print("\n" + printMessage)
        print(f"General Output: {output}")
        
    if monitor:
        influx = Influx()
        influx.connectInflux()
        
        queue = multiprocessing.Queue()
        signalProcess = multiprocessing.Process(target = tcpConnection, args = (queue,))
        signalProcess.daemon = True
        
        signalProcess.start()
        
        list_setups = [jsonConfigs.get("setup_1"), jsonConfigs.get("setup_2")]
        
        if influx.checkConnection():
            while True:
                for i in range(0, len(list_setups)):
                
                    """Check for interlock signal"""
                    if not queue.empty():
                        msg = queue.get_nowait()
                        interlock_state = msg[0]
                        if interlock_state:
                            doInterlock(hmp4040, msg[1])
                            
                    """Upload vdd and vda data to influx"""
                    setup = list_setups[i]
                    for source in setup:
                        channel = setup.get(source)
                        if channel != -1:
                            hmp4040.selectChannel(channel)
                            
                            current = float(hmp4040.measureCurrent())
                            time_curr_now = time.time()
                            datum_current = [current, time_curr_now]
                        
                            voltage = float(hmp4040.measureVoltage())
                            time_volt_now = time.time()
                            datum_voltage = [voltage, time_volt_now]
                        
                            if hmp4040.checkError():
                                print("\33[30;101m" + "Error: " + hmp4040.errorMessage[0:-1] + " Command: " + hmp4040.command[0:-1] + "\33[0m")
                                hmp4040.setChannel(False)
                                #sys.exit(1)
                                
                            # influx.writeInflux(source[0:3] + "_current_" + str(i + 1), datum_current)
                            # influx.writeInflux(source[0:3] + "_voltage_" + str(i + 1), datum_voltage)
                            influx.writeInflux("Module_current_" + str(i + 1), datum_current, i + 1)
                            influx.writeInflux("Module_voltage_" + str(i + 1), datum_voltage, i + 1)
                            
                time.sleep(0.33)
                
        #signalProcess.join()
                
if __name__ == "__main__":
    main(sys.argv)



