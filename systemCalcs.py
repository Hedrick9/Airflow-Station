# This script is for all necessary calculations (Flow, Energy, etc.)
import math
import numpy as np
#______________________________________________________________________________
##############################################################################
# UNIT CONVERSIONS
##############################################################################
Cum_to_Cuft = 35.3146667
Kg_to_lb = 2.20462
Kwh_to_Kbtu = 3.41214
millibar_to_inHg = 0.02953
millibar_to_psf = 2.08854
millibar_to_psi = 0.0145038
inW_to_inHg = 0.0736912
##############################################################################
# Velocity Pressure
def velocity(Pv, rho):
    
    V = 1096.5 * math.sqrt(abs(Pv/rho))
    return V

# Actual Volumetric Flowrate - Numerical Evaluation of Duct Volumetric Flow Rate
def QflowActual(V, D):
    # Cross-sectional area for circular duct of dimension 
    r = (D/2)/12
    A = math.pi * r**2 
    Q = V * A 
    return Q

# Standard Volumetric Flowrate - The flow rate that would exist if the air were
# at standard air density conditions. 
def QflowStandard(Q, P, T):
    Pstandard = 30 # inHg
    Pactual = P
    Tstandard = 288.72 # 60 degF
    Tactual = ((T - 32)/1.8) + 273.15
    Qs = Q*(Pactual/Pstandard)*(Tstandard/Tactual)
    return Qs

# Partial Pressure (Water Vapor) - ASHRAE Fundamentals 1.12 eq (6) 
def Pp(Tdew):
    T = Tdew + 459.67 # Convert from degF to deg Rankine (absolute temperature)
    c1 = -1.0440397e4
    c2 = -1.1294650e1
    c3 = -2.7022355e-2
    c4 = 1.2890360e-5
    c5 = -2.4780681e-9
    c6 = 6.5459673

    pp = np.exp((c1/T)+c2+(c3*T)+(c4*T**2)+(c5*T**3)+(c6*np.log(T))) * 2.03602 # psia to inHg -> for psia to mbar: 68.9475728 
    return pp

# Humidity Ratio (mixing ratio) - Mass of Water Vapor to Mass of Dry Air
def W(Pbar, pp):

    w = 0.621945*(pp/(Pbar-pp))
    return w

# Relative Humidity 
def RH(pp_water, pp_sat):
    # Calculate relative humidity in %
    rh = 100 * (pp_water/pp_sat)
    return rh

# Moist Air Density
def rho(Pbar, T, W):
    # Calculate the density of the air in the chamber based on moist air calculations
    Temp = T + 459.69 # Temp. in Rankine
    P = Pbar * millibar_to_psf
    rho = (P * (1 + W))/(53.352 * Temp * (1 + 1.6078 * W))
    return rho

# Differential Pressure Sensor
def pdiff_setra(Aout, lo_r, hi_r):
    # Calculate pdiff in inWc based on current output from Setra sensor
    m = (hi_r - lo_r)/(20 - 4) # slope for current to pressure line eqtn.
    b = 4*m
    y = m*Aout - b

    return y

# Dew Point meter (Model DewTran-W)
def DP_DewTran(Aout, lo_r, hi_r):
    # Calculate Dew Point Temperature in deg F based on current output from DewTran meter
    m = (hi_r - lo_r)/(20 - 4)
    b = (4*m) - lo_r
    y = m*Aout - b
    DP_T = (y*1.8) + 32 # deg C -> deg F
    return DP_T


if __name__ == "__main__":
    
    Pv = float(input("User input measured velocity pressure:\n"))
    Aout = 8.05
    Pbar = 29.60*33.864 # Barometric Pressure in mbar 
    pp_ = Pp(56.5) 
    W_ = W(29.60, pp_) 
    rho_ = rho(Pbar, 75.9, W_)
    V_ = velocity(Pv, rho_)
    Q_ = QflowActual(V_, 16)
    pdiff_ = pdiff_setra(Aout, 0, 0.5)

    print("Calculated flow rate: {} cfm".format(round(Q_, 2)))
    print(pdiff_)
