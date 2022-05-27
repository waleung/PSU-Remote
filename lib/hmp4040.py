import pyvisa
import sys
import colorama

class HMP4040():
    """Class for control of a r&S hmp4040 psu"""
    
    def __init__(self, visa_name):
        self.rm = pyvisa.ResourceManager()
        self.hmp4040 = self.rm.open_resource(visa_name)
        self.errorMessage = ""
        self.error = False
        self.command = ""
        colorama.init()
            
    def _writeMessage(self, message):
        self.command = message
        self.hmp4040.write(message)
        self.checkError()
        return message
            
    def _queryMessage(self, message):
        self.command = message
        query = self.hmp4040.query(message)
        #self.checkError()
        #self.command = message
        return query
        
    def getResources(self):
        return self.rm.list_resources()
        
    def getError(self):
        return self._queryMessage("SYST:ERR?")
        
    def getEventStatusRegister(self):
        return self._queryMessage("*ESR?")
        
    def checkError(self):
        status = int(self.getEventStatusRegister())
        if (status & 0x3C) > 0:
            self.errorMessage = self.getError()
            self.error = True
        else:
            self.error = False
            
        return self.error
        
        
    """-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""
        
    def selectChannel(self, channel):
        """Select channel"""
        return self._writeMessage("INST " + "OUT" + str(channel))
        
    def setChannel(self, enable):
        """Activate the current selected channel (For output). True to enable, False to disable"""
        state = int(enable)
        return self._writeMessage("OUTP:SEL " + str(state))
        
    def setOutput(self, enable):
        """Turn on all active channels. True to enable, False to disable"""
        state = int(enable)
        return self._writeMessage("OUTP:GEN " + str(state))
        
    def measureCurrent(self):
        """Measure the current on the selected channel"""
        return self._queryMessage("MEAS:CURR?")
        
    def measureVoltage(self):
        """Measure the voltage on the selected channel"""
        return self._queryMessage("MEAS:VOLT?")
        
    def setCurrent(self, current):
        """Set the current on the selected channel"""
        return self._writeMessage("CURR " + str(current))
        
    def setVoltage(self, voltage):
        """Set the voltage on the selected channel"""
        return self._writeMessage("VOLT " + str(voltage))
        
    def enableSystemMix(self):
        """Enables remote control without locking manual control"""
        return self._writeMessage("SYST:MIX")
        
    def enableSystemLocal(self):
        """Enables manual control. Will return remote control back to manual control"""
        return self._writeMessage("SYST:LOC")
        
    def enableSystemRemote(self):
        """Set system to remote state. Will lock manual controls"""
        return self_writeMessage("SYST:REM")
        
    def displayVoltage(self):
        """Queries the output voltage of selected channel"""
        return self._queryMessage("VOLT?")
        
    def displayCurrent(self):
        """Queries the output current of selected channel"""
        return self._queryMessage("CURR?")
        
    def displayChannel(self):
        """Queries the current selected channel"""
        return self._queryMessage("INST:NSEL?")
    
    def displayActiveChannel(self):
        """Queries about the active channel"""
        return self._queryMessage("OUTP:SEL?")
        
    def displayOutput(self):
        """Queries the current selected channel"""
        return self._queryMessage("OUTP:GEN?")
     
        
        
    
