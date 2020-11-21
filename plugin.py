"""
<plugin key="KinCony_KC868" name="KinCony KC868 plugin" author="Blindlight" version="1.0.0" 
externallink="https://www.kincony.com/product/relay-controller">
    <description>
        <h2>KinCony KC868</h2><br/>
    </description>
    <params>
        <param field="Address" label="Adresse IP" width="150px" required="true" />
        <param field="Port" label="Port" width="80px" required="true" default="4196" />
        <param field="Mode1" label="Model" width="100px" required="true">
            <options>
                <option label="KC868-H32" value="32 6" />
                <option label="KC868-H16" value="16 8" />
                <option label="KC868-H8" value="8 8" />
                <option label="KC868-H4" value="4 8" />
                <option label="KC868-H2" value="2 0" />
            </options>
        </param>
        <param field="Mode2" label="Control All" width="80px">
            <options>
                <option label="True" value="True" />
                <option label="False" value="False" default="true" />
            </options>
        </param>
        <param field="Mode3" label="Input Ignore Interval(s)" default ="10" width="80px" />
        <param field="Mode4" label="Debug" width="80px">
            <options>
                <option label="None" value="0"  default="true" />
                <option label="Python Only" value="2"/>
                <option label="Basic Debugging" value="62"/>
                <option label="Basic+Messages" value="126"/>
                <option label="Connections Only" value="16"/>
                <option label="Connections+Queue" value="144"/>
                <option label="All" value="-1"/>
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import time
from math import ceil

class BasePlugin:
    
    def __init__(self):
        self.input_states = {}
        self.output_states = {}
        self.input_update_time = {}
        self.input_ignore_interval = 10
        return

    def onStart(self):
        self.nb_relay, self.nb_input = (int(x) for x in Parameters["Mode1"].split())
        Domoticz.Debugging(int(Parameters["Mode4"]))
        self.input_ignore_interval = int(Parameters["Mode3"])
        # DumpConfigToLog()
        self.KCConn = Domoticz.Connection(Name="Kincony", Transport="TCP/IP", Address=Parameters["Address"], Port=Parameters["Port"])
        self.KCConn.Connect()

    def onStop(self):
        if self.KCConn.Connected():
            self.KCConn.Disconnect()
            Domoticz.Log("KC868 plugin is stopping.")
        pass

    def onConnect(self, Connection, Status, Description):
        if (Status == 0):
            Domoticz.Log("KC868 is connected.")
            if (len(Devices) == 0):
                Domoticz.Debug("Create device. Input number : " + str(self.nb_input) + ", Relay number : " + str(self.nb_relay))
                for relay in range(1, self.nb_relay + 1):
                    Domoticz.Device(Unit=relay, Name="Relay " + str(relay), TypeName="Switch", Used=1).Create()
                if Parameters["Mode2"]:
                    Domoticz.Device(Unit=33, Name=f"Relays All", TypeName="Switch", Used=1).Create()
                for input in range(1, self.nb_input + 1):
                    Domoticz.Device(Unit=(input+40), Name="Input " + str(input), Type=244, Subtype=73, Switchtype=2, Used=1).Create()
            if (len(Devices) > 0):
                self.KCReadOutputs()
                self.UpdateDomoticz(False, False)
                self.KCReadInputs()
                self.UpdateDomoticz(True, False)
        else:
            Domoticz.Log("Failed to connect ("+str(Status)+") to: "+Parameters["Address"]+":"+Parameters["Port"]+" with error: "+Description)
    
    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called. Unit: " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level) + ", Hue:" + str(Hue))
        if self.KCConn.Connected():
            if Unit <= 32:
                self.KCWriteOutput(str(Unit), str(Command))
            elif Unit == 33:
                if str(Command) == "On":
                    self.KCTurnAllOn()
                elif str(Command) == "Off":
                    self.KCTurnAllOff()
            self.UpdateDomoticz(False, True)
    
    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")
        if self.KCConn.Connected():
            Domoticz.Debug("KC868 is alive")
        else:
            Domoticz.Log("KC868 is reconnecting")
            self.KCConn.Connect()
        self.KCReadInputs()
        

    def onMessage(self, Connection, Data):
        msg_recv = Data.decode("utf-8")
        iupdate_flag = False
        oupdate_flag = False
        if "RELAY-GET_INPUT-255" in msg_recv:
            if "OK" in msg_recv:
                state_str = bin(int(msg_recv.split(',')[1]))[2:][::-1]
                state_str = state_str + '0' * (8 - len(state_str))
                for i in range(1, self.nb_input+1):
                    self.input_states[i] = int(state_str[i-1])
                iupdate_flag = True
            elif "ERROR" in msg_recv:
                Domoticz.Log(f"Get input states error")
        elif "RELAY-STATE-255" in msg_recv:
            if "OK" in msg_recv:
                if len(msg_recv.split(','))-2 != self.nb_relay/8:
                    Domoticz.Log(f"Maybe you selected a wrong model, the states num is {(len(msg_recv.split(','))-2)*8}, the selected model gets {self.nb_relay} relays.")
                state_str = ''
                for state in msg_recv.split(',')[1:-1]:
                    str_temp = '0' * (8 - len(bin(int(state))[2:])) + bin(int(state))[2:]
                    state_str += str_temp
                state_str = state_str[::-1]
                for i in range(1, self.nb_relay+1):
                    self.output_states[i] = int(state_str[i-1])
                oupdate_flag = True
            elif "ERROR" in msg_recv:
                Domoticz.Log(f"Get relay states error")
        elif "RELAY-ALARM" in msg_recv:
            temp_l = msg_recv.split("M-")
            for s in temp_l:
                if "OK" in s:
                    input_num = int(s[0])
                    Domoticz.Debug(f"input_num:{input_num}")
                    Domoticz.Debug(f"{self.input_update_time}")
                    try:
                        last_update = self.input_update_time[input_num]
                        if type(last_update) == float:
                            if time.time()-last_update >= self.input_ignore_interval:
                                self.input_update_time[input_num] = time.time()
                                self.input_states[int(input_num)] = 0
                                iupdate_flag = True
                    except:
                        self.input_update_time[input_num] = time.time()
                        self.input_states[int(input_num)] = 0
                        iupdate_flag = True
        elif "RELAY-KEY-255" in msg_recv:
            if "OK" in msg_recv:
                self.output_states[int(msg_recv.split(',')[1])] = int(msg_recv.split(',')[2])
                oupdate_flag = True
            elif "ERROR" in msg_recv:
                Domoticz.Log(f"Get relay{msg_recv.split(',')[1]} state error")
        elif "RELAY-SET-255" in msg_recv:
            if "OK" in msg_recv:
                self.output_states[int(msg_recv.split(',')[1])] = int(msg_recv.split(',')[2])
                oupdate_flag = True
            elif "ERROR" in msg_recv:
                Domoticz.Log(f"Get relay{msg_recv.split(',')[1]} state error")
        elif "RELAY-SET_ALL-255" in msg_recv:
            if "OK" in msg_recv:
                if len(msg_recv.split(','))-2 != self.nb_relay/8:
                    Domoticz.Log(f"Maybe you selected a wrong model, the states num is {(len(msg_recv.split(','))-2)*8}, the selected model gets {self.nb_relay} relays.")
                state_str = ''
                for state in msg_recv.split(',')[1:-1]:
                    str_temp = '0' * (8 - len(bin(int(state))[2:])) + bin(int(state))[2:]
                    state_str += str_temp
                state_str = state_str[::-1]
                for i in range(1, self.nb_relay+1):
                    self.output_states[i] = int(state_str[i-1])
                oupdate_flag = True
            elif "ERROR" in msg_recv:
                Domoticz.Log(f"Set relay states error")
        elif "RELAY-AON-255,1,1" in msg_recv:
            if "OK" in msg_recv:
                for i in range(1, self.nb_relay+1):
                    self.output_states[i] = 1
                oupdate_flag = True
            elif "ERROR" in msg_recv:
                Domoticz.Log(f"Set all relays on error")
        elif "RELAY-AOF-255,1,1" in msg_recv:
            if "OK" in msg_recv:
                for i in range(1, self.nb_relay+1):
                    self.output_states[i] = 0
                oupdate_flag = True
            elif "ERROR" in msg_recv:
                Domoticz.Log(f"Set all relays on error") 
        self.UpdateDomoticz(iupdate_flag, oupdate_flag)

    def KCReadInputs(self):
        Domoticz.Debug("KinconyReadInputs called: 'RELAY-GET_INPUT-255'")
        KinconyTx = "RELAY-GET_INPUT-255"
        self.KCConn.Send(KinconyTx)

    def KCReadOutputs(self):
        Domoticz.Debug("KinconyReadOutputs called : 'RELAY-STATE-255'")
        KinconyTx = "RELAY-STATE-255"
        self.KCConn.Send(KinconyTx)

    def KCWriteOutput(self, Output, Value):
        KinconyTx = "RELAY-SET-255," + Output + "," + ("1" if Value == "On" else "0")
        self.KCConn.Send(KinconyTx)
        Domoticz.Debug("KinconyWriteOutput - Sent :'" + KinconyTx + "'")

    def KCWriteAllOutputs(self, *Value):
        if len(Value) < ceil(self.nb_relay / 8):
            Domoticz.Error("KinconyWriteAllOutputs - Error : states are less than relays.")
            return
        KinconyTx = "RELAY-SET_ALL-255,"
        for i in range(0,len(Value)):
            KinconyTx = KinconyTx + str(Value[i]) + ","
        KinconyTx = KinconyTx[:-1]
        self.KCConn.Send(KinconyTx)
        Domoticz.Debug("KinconyWriteAllOutputs - Sent : '" + KinconyTx + "'")

    def KCTurnAllOn(self):
        KinconyTx = "RELAY-AON-255,1,1"
        self.KCConn.Send(KinconyTx)
        Domoticz.Debug("KinconyTurnAllOn - Sent")

    def KCTurnAllOff(self):
        KinconyTx = "RELAY-AOF-255,1,1"
        self.KCConn.Send(KinconyTx)
        Domoticz.Debug("KinconyTurnAllOff - Sent")

    def UpdateDomoticz(self, Inputs, Outputs):
        Domoticz.Debug("UpdateDomoticz - call (inputs = " + ("yes" if Inputs else "no") + " outputs = " + ("yes" if Outputs else "no") + ")")
        if Inputs:
            Domoticz.Debug(f"Input states: {self.input_states}")
            if len(self.input_states) != 0:
                for input in range(41, self.nb_input + 41):
                    input_state = "Open" if self.input_states[input-40] == 0 else "Closed"
                    if input_state != Devices[int(input)].sValue:
                        Domoticz.Debug(f"UpdateDomoticz - Input value: Unit:{str(input)} nValue: {Devices[int(input)].nValue} to {0 if self.input_states[input-40] == 1 else 1}")
                        Domoticz.Debug(f"sValue: {Devices[int(input)].sValue} to {input_state}")
                        Devices[int(input)].Update(nValue = 0 if self.input_states[input-40] == 1 else 1, sValue = input_state)
        if Outputs:
            Domoticz.Debug(f"Relay states: {self.output_states}")
            if len(self.output_states) != 0:
                aon_flag = 1
                for i in range(1, self.nb_relay+1):
                    Domoticz.Debug(f"relay{i}: {self.output_states[i]}")
                    aon_flag = aon_flag * self.output_states[i]
                if not aon_flag:
                    Devices[33].Update(nValue=0, sValue = "Off")
                else:
                    Devices[33].Update(nValue=1, sValue = "On")
                for relay in range(1, self.nb_relay+1):
                    output_state = "On" if self.output_states[relay] == 1 else "Off"
                    if output_state != Devices[int(relay)].sValue:
                        Domoticz.Debug(f"UpdateDomoticz - Relay value: Unit:{str(relay)} nValue: {Devices[int(relay)].nValue} to {self.output_states[relay]}")
                        Domoticz.Debug(f"sValue: {Devices[int(relay)].sValue} to {output_state}")
                        Devices[int(relay)].Update(nValue = self.output_states[relay], sValue = output_state)

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

    ## Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Log( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Log("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Log("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Log("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Log("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Log("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Log("Device LastLevel: " + str(Devices[x].LastLevel))
    return