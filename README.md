# PSU-Remote

## Installation
Install NI-VISA from here: <br>
https://www.ni.com/en-no/support/downloads/drivers/download.ni-visa.html#442805 <br>

HMP4040 need drivers. Install it from the Driver folder. <br>

Install anaconda and create environment from environment.yml. <br>
````bash
conda env create -f environment.yml
conda activate PSU_REMOTE
````

## Usage
Setup influxdb in config\influxdb.json <br>
````database```` key is for test setup 1 <br>
````database_2```` key is for test setup 2 <br>

Use hmp4040.json to configure the channels to monitor <br>

Example of usage: <br>
````python
python hmp4040_remote.py -s 1 -m #Sets the system to Mixed mode and start logging to influx db
python hmp4040_remote.py -c 2 -v 10 -i 3.4 -o #Selects channel 2, sets the voltage to 10V and current to 3.4A

python ki2450_remote.py -v 10 -i 3.4 -o #Sets voltage to 10V and current to 3.4A. Then turns the output on.
````
 
For VI_scan and IV_scan, need to change settings in the files. <br>
Example: <br>
````python
"""---------------------------------------------------------------------------------------------------------------------------------"""
CHANNEL = 1
VOLTAGE_LIMIT = 2
CURRENT_START = 3.75
CURRENT_END = 0.1
CURRENT_STEPS = 0.1
TIME_IN_STEPS = 1
TIME_BETWEEN_STEPS = 1
MODE = 1 # Regular ramping: (0) / Switch on and off: (1)
INFLUX = 0 # Enable (1) or disable (0) upload to influxdb
LOCAL = 1 # Enable (1) or disable (0) saving data locally
RESOURCE_NAME = 'ASRL6::INSTR' # VISA resource name. Can be found using pyvisa.ResourceManager
MODULE_NUMBER = "RD53AE1003"
TEMPERATURE = "20C"
"""---------------------------------------------------------------------------------------------------------------------------------"""
````
