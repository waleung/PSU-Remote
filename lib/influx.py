import json
import time
import os.path
import influxdb_client
from influxdb_client import WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS  


class Influx():
    """Influx class handles the logging of data and connections from PCTM to an Influx db. """
    
    def __init__(self):
        self.client = influxdb_client.InfluxDBClient(url="", token = "", org = "")
        self.write_api = self.client.write_api(write_options=ASYNCHRONOUS)
        self.influx_details = None
        
    def getInflux(self):
        with open(os.path.dirname(__file__) + "/../configs/influxdb.json") as file:
            self.influx_details = json.load(file)
            
    def connectInflux(self):
        self.getInflux()
    
        if self.influx_details.get('username') == "":
            token_new = self.influx_details['password']
        else:
            token_new = f"{self.influx_details['username']}:{self.influx_details['password']}"
    
        self.client = influxdb_client.InfluxDBClient(
            url=f"{self.influx_details['host']}:{self.influx_details['port']}",
            token = token_new,
            org = self.influx_details['organization'])
        
        self.write_api = self.client.write_api(write_options=ASYNCHRONOUS)
        
    def writeInflux(self, source, datum):
        dataPoint = influxdb_client.Point(self.influx_details['measurement']).tag("location", self.influx_details['location']).field(source, datum[0]).time(int(datum[1]*1000), write_precision=WritePrecision.MS)
        write_results = self.write_api.write(bucket=f"{self.influx_details['database']}", record=dataPoint)
        try:
            write_results.get()
        except:
            raise

    def checkConnection(self):
        try:
            health = self.client.health()
        except:
            raise 
         
        if health.status == "pass":
            print(f"Influx DB found at {self.influx_details['host']}:{self.influx_details['port']}")
            try:
                print(f"Connecting to Influx DB at {self.influx_details['host']}:{self.influx_details['port']}")
                dataPoint = influxdb_client.Point(self.influx_details['measurement'])
                write_results = self.write_api.write(bucket=f"{self.influx_details['database']}", record=dataPoint)
                write_results.get()
                return True
            except Exception as e:
                if str(e)[1:4] == "400": #Ignore Error Code 400. 
                    return True
                else:
                    raise
        else:
            print(f"Failed to find an Influx DB at {self.influx_details['host']}:{self.influx_details['port']}: {health.message}")
            
        

        
        