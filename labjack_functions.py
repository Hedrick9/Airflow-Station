from labjack import ljm
import math

def K_to_F(T):
    # Kelvin to Celsius
    C = T - 273.15
    # Celcius to Fahrenheit
    F = (C*(9/5)) + 32

    return F

def V_to_P(v):
    # Voltage to Pressure, provided a given line equation
    p = -0.026386*v + 0.1236

    return round(p, 2)

# ---- READ IN SINGLE END or DIFF. THERMOCOUPLE MEASUREMENT --------------------------
def tempRead_TC(ch_p, ch_n=199, offset=0, tc_type=22):

    # Open first available LabJack connection
    handle = ljm.openS("ANY", "ANY", "ANY")

    names = ["AIN{}_EF_INDEX".format(ch_p), "AIN{}_EF_CONFIG_A".format(ch_p),
             "AIN{}_NEGATIVE_CH".format(ch_p)]
    # tc_type: 21-J, 22-K, 23-R, 24-T
    aValues = [tc_type, 2, ch_n] # Configuration inputs

    numFrames = len(names)
    ljm.eWriteNames(handle, numFrames, names, aValues)

    name = "AIN{}_EF_READ_A".format(ch_p)
    r_ = ljm.eReadName(handle, name)
    T = round(r_ + offset, 2)

    ljm.close(handle)

    return T

# ---- READ IN SINGLE END or DIFF. THERMOCOUPLE MEASUREMENT w/ CJC ------------
def tempRead_TC_CJC(ch_p, ch_n=199, ch_cjc=0, offset=0):
    
    modbus_add = ch_cjc*2
    CJC_slope = 55.56
    CJC_offset = 255.37
    # Open first available LabJack connection
    handle = ljm.openS("ANY", "ANY", "ANY")

    names = ["AIN{}_EF_INDEX".format(ch_p), "AIN{}_EF_CONFIG_A".format(ch_p),
             "AIN{}_EF_CONFIG_B".format(ch_p), "AIN{}_EF_CONFIG_D".format(ch_p),
             "AIN{}_EF_CONFIG_E".format(ch_p), "AIN{}_NEGATIVE_CH".format(ch_p)]
    
    # Configuration inputs
    aValues = [22, 2, modbus_add, CJC_slope, CJC_offset, ch_n]

    numFrames = len(names)
    ljm.eWriteNames(handle, numFrames, names, aValues)

    name = "AIN{}_EF_READ_A".format(ch_p)
    r_ = ljm.eReadName(handle, name)
    T = round(r_, 2)

    ljm.close(handle)

    return T

# ---- READ IN SINGLE RTD MEASUREMENT -----------------------------------------
def tempRead_RTD(ai_ch, rtd=40, offset=0):


    # Open first available LabJack connection
    handle = ljm.openS("ANY", "ANY", "ANY")
    # AIN# values:
    #   RTD Type: 40 = PT100, 41 = PT500, 42 = PT1000
    #   Temperature Units: 0 = K, 1 = C, 2 = F
    #   
    names = ["AIN{}_EF_INDEX".format(ai_ch), "AIN{}_EF_CONFIG_A".format(ai_ch),
             "AIN{}_NEGATIVE_CH".format(ai_ch)]
    
    aValues = [rtd, 2] # Configuration inputs

    numFrames = len(names)
    ljm.eWriteNames(handle, numFrames, names, aValues)

    name = "AIN{}_EF_READ_A".format(ai_ch)
    r_ = ljm.eReadName(handle, name)
    T = round(r_, 2)

    ljm.close(handle)

    return T

# ---- READ IN SINGLE ANALOG INPUT CHANNEL ------------------------------------
def aiRead(channel_p, channel_n=199, v_range=10.0):

    # Open first available LabJack connection
    handle = ljm.openS("ANY", "ANY", "ANY")
    # AIN0 and AIN1:
    #   Negative channel = single ended (199)
    #   Range: +/- 10.0 V (10.0)
    #   Resolution index = Default (0)
    #   Settling, in microseconds = Auto (0)
    names = ["AIN{}_NEGATIVE_CH".format(channel_p), "AIN{}_RANGE".format(channel_p),
             "AIN{}_RESOLUTION_INDEX".format(channel_p), "AIN{}_SETTLING_US".format(channel_p)]

    aValues = [channel_n, v_range, 0, 0]
    numFrames = len(names)
    ljm.eWriteNames(handle, numFrames, names, aValues)
    
    name = "AIN{}".format(channel_p)
    result = ljm.eReadName(handle, name)
    ljm.close(handle)

    return result

# ---- READ IN FROM MULTIPLE ANALOG INPUT CHANNELS ----------------------------
def aiReads(a1, a2):

    # Open first found LabJack
    handle = ljm.openS("ANY", "ANY", "ANY")
    # AIN0 and AIN1:
    #   Negative channel = single ended (199)
    #   Range: +/- 10.0 V (10.0)
    #   Resolution index = Default (0)
    #   Settling, in microseconds = Auto (0)
    names = ["AIN{}_NEGATIVE_CH".format(a1), "AIN{}_RANGE".format(a1),
             "AIN{}_RESOLUTION_INDEX".format(a1), "AIN{}_SETTLING_US".format(a1),
             "AIN{}_NEGATIVE_CH".format(a2), "AIN{}_RANGE".format(a2), 
             "AIN{}_RESOLUTION_INDEX".format(a2), "AIN{}_SETTLING_US".format(a2)]
    aValues = [199, 10.0, 0, 0,
               199, 10.0, 0, 0]
    numFrames = len(names)
    ljm.eWriteNames(handle, numFrames, names, aValues)
    
    names = ["AIN{}".format(a1), "AIN{}".format(a2)]
    numFrames = len(names)
    results = ljm.eReadNames(handle, numFrames, names)
    ljm.close(handle)

    return results[0], results[1]
# --- READ IN FROM LJTick - Current Shunt SENSOR (AI Current to AI Voltage)----
# The LJTick-CurrentShunt is a signal conditioning module designed to convert
# 4-20 mA current loop signals into voltage signals that vary from 0.472 to 2.36 V.
def aiCurrent(channel_p, v_range=2.36):

    # Open first available LabJack connection
    handle = ljm.openS("ANY", "ANY", "ANY")
    # AIN0 and AIN1:
    #   Negative channel = single ended (199)
    #   Range: +/- 10.0 V (10.0)
    #   Resolution index = Default (0)
    #   Settling, in microseconds = Auto (0)
    names = ["AIN{}_NEGATIVE_CH".format(channel_p), "AIN{}_RANGE".format(channel_p),
             "AIN{}_RESOLUTION_INDEX".format(channel_p), "AIN{}_SETTLING_US".format(channel_p)]

    aValues = [199, v_range, 0, 0]
    numFrames = len(names)
    ljm.eWriteNames(handle, numFrames, names, aValues)
    
    name = "AIN{}".format(channel_p)
    voltage = ljm.eReadName(handle, name)
    current = voltage * 8.4746 # Converts volts to mA [I = V / (20 * 5.9ohms)]
    ljm.close(handle)

    return voltage, current
# -----------------------------------------------------------------------------
if __name__ == '__main__':

#    print(tempRead_TC(0))
    print(tempRead_TC(0,1))
    print(tempRead_TC(6,7,0,24))
#    print(tempRead_TC_CJC(4,5,6))
#    print(tempRead_TC_CJC(0,1,6))
#    print(aiRead(2,3))
