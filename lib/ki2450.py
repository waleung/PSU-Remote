import pyvisa
import sys
import colorama

class KI2450():
    """Class for control of a Keithley 2450 psu"""
    
    def __init__(self, visa_name):
        self.rm = pyvisa.ResourceManager()
        self.ki2450 = self.rm.open_resource(visa_name)
        self.errorMessage = ""
        self.error = False
        self.command = ""
        colorama.init()
            
    def _writeMessage(self, message):
        self.command = message
        self.ki2450.write(message)

        if self.checkError():
            self.safeExit()
        
        return message
        
    def _queryMessage(self, message):
        self.command = message
        query = self.ki2450.query(message)
        if self.checkError():
            self.safeExit()
        return query
        
    def getResources(self):
        return self.rm.list_resources()
        
    def getError(self):
        return self._queryMessage("SYST:ERR?")

    def getEvent(self):
        return self.ki2450.query("SYST:EVEN:NEXT?")
        
    def getEventStatusRegister(self):
        return self._queryMessage("*STB?")
        
    def checkError(self):
        self.error = False
        errorcode = 1
        while errorcode != 0:
            event = self.getEvent()
            errorcode = int(event[0:event.find(",")])
            if (errorcode < 0):
                self.errorMessage = event[event.find('\"'):]
                print("\33[30;101m" + "Error: " + self.errorMessage[0:-1] + " Command: " + self.command + "\33[0m")
                self.error = True
            elif (errorcode > 0):
                self.errorMessage = event[event.find('\"'):]
                print("\33[30;103m" + "Warning: " + self.errorMessage[0:-1] + "\33[0m")

        return self.error

    def safeExit(self, sig = None, frame = None):
        self.ki2450.write("OUTP 0")
        print("Setting Output Off")
        sys.exit(1)
        
    """-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""     
    def setOutput(self, enable):
        """Turn on Output. True to enable, False to disable"""
        state = int(enable)
        return self._writeMessage("OUTP " + str(state))
        
    def setSource(self, source):
        """Set to output current or voltage"""
        return self._writeMessage("SOUR:FUNC " + source)
        
    def setAutoRange(self, enable):
        """Turn autorange on or off"""
        state = int(enable)
        return self._writeMessage("CURR:RANG:AUTO " + str(state))
     
    def measureCurrent(self):
        """Measure the current"""
        return self._queryMessage("MEAS:CURR?")
        
    def measureVoltage(self):
        """Measure the voltage"""
        return self._queryMessage("MEAS:VOLT?")
        
    def setCurrentCompliance(self, current):
        """Set the current limit when the source is voltage"""
        return self._writeMessage("SOUR:VOLT:ILIMIT " + str(current))
        
    def setVoltageCompliance(self, voltage):
        """Set the voltage limit when the source is current"""
        return self._writeMessage("SOUR:CURR:VLIMIT " + str(voltage))
        
    def setVoltage(self, voltage):
        """Set the source voltage"""
        return self._writeMessage("SOUR:VOLT " + str(voltage))
        
    def setCurrent(self, current):
        """Set the source current"""
        return self._writeMessage("SOUR:CURR " + str(current))

    def displayVoltage(self):
        """Queries the set output voltage"""
        return self._queryMessage("SOUR:VOLT?")
        
    def displayCurrent(self):
        """Queries the set output current """
        return self._queryMessage("SOUR:CURR?")
        
    def displayOutput(self):
        """Queries the main output """
        return self._queryMessage("OUTP?")
        
    def displayCurrentLimit(self):
        """Queries the set limit of current (Compliance)"""
        return self._queryMessage("SOUR:VOLT:ILIMIT?")
        
    def displayVoltageLimit(self):
        """Queries the set limit of voltage"""
        return self._queryMessage("SOUR:CURR:VLIMIT?")
        
        
    
