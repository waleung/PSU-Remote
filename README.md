# PSU-Remote

## Installation
Install NI-VISA from here: <br>
https://www.ni.com/en-no/support/downloads/drivers/download.ni-visa.html#442805 <br>

HMP4040 need drivers. Install it from the Driver folder. <br>

Install conda and create environment from environment.yml. <br>
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
python hmp4040_remote.py -s 1 -m 
python hmp4040_remote.py -c 2 -v 10 -i 3.4 -o 

python ki2450_remote.py -v 10 -i 3.4 -o
````
 
For VI_scan and IV_scan, need to change settings in the files. <br>
