# PSU-Remote

Install NI-VISA from here: <br>
https://www.ni.com/en-no/support/downloads/drivers/download.ni-visa.html#442805 <br>

HMP4040 need drivers. Install it from the Driver folder. <br>

Install conda and create environment from environment.yml. <br>
Use "conda env create -f environment.yml" <br>
conda activate PSU_REMOTE <br>

------------------------------------------------------------------------------------- <br>
Setup influxdb in config\influxdb.json <br>
"database 1" is for test setup 1 <br>
"database 2" is for test setup 2 <br>

configure channel to monitor in hmp4040.json. <br>

Example of usage: <br>
python hmp4040_remote.py -s 2 -m <br>
python hmp4040_remote.py -c 2 -v 10 -i 3.4 -o <br>

python ki2450_remote.py -v 10 -i 3.4 -o <br>
 
For VI_scan and IV_scan, need to change settings in the files. <br>
