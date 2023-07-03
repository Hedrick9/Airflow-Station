"""
Description: 
The following is a script that computes various airflow and heat gain metrics
based on input parameters provided by the user in a csv file. Input parameters
are loaded from csv to a pandas dataframe.

Dependencies:
    - pandas
    - numpy
    - os (standard library)
"""
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                               Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import systemCalcs as calc 
import pandas as pd
import csv 
import os
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def write_data(data, file_name):
    with open(file_name, 'a', newline='') as file_data:
        csvWriter = csv.writer(file_data, delimiter=',')
        csvWriter.writerow(data)


# operation to get string of current directory path
current_directory = os.getcwd()
# Read input parameters from csv file
csv_file_name = "input_parameters.csv"
csv_path = current_directory + '/' + csv_file_name
df = pd.read_csv(csv_path)

# Input parameters ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 1.) Barometric Pressure - inHg
Pbar_inHg = df["Pbar_inHg"][0]
# 2.) Barometric Pressure converted from inHg to millibars 
Pbar_mbar = Pbar_inHg/calc.millibar_to_inHg
# 3.) Duct diameter (ID used for flow calculation)
duct_diameter = df["duct diameter"][0]
# 4.) Differential pressure measured in in.wc. (Velocity pressure)
pdiff = df["dp.inw"][0]
# 5.) Dry bulb temperature
Tdb = df["Tdb"][0]
# 6.) Dew point temperature
Tdew = df["Tdew"][0]
# ~~ Optional inputs ~~
# 7.) Room Dry Bulb Temperature
Tdb_room = df["Tdb_room"][0]
# 8.) Room Humidity Ratio
W_room = df["W_room"][0]
# Outputs ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 1.) Partial Pressure Water Vapor (Calculated)
pp_water = calc.Pp(Tdew)
# 2.) Humidity Ratio - Supply/Room
w = calc.W(Pbar_inHg, pp_water)
# 3.) Calculated Air Density - Room/Supply System 1
rho = calc.rho(Pbar_mbar, Tdb, w) 
# 4.) Air Velocity
V = calc.velocity(pdiff, rho)
# 5.) Actual Measured Flow [Acfm] - Provide duct ID 
Q_Acfm = round(calc.QflowActual(V, duct_diameter), 2) 
# 6.) Standard Air Corrected Flow [Scfm]
Q_Scfm = round(calc.QflowStandard(Q_Acfm, Pbar_inHg, Tdb), 2)
# 7.) Sensible Heat Gain [Btu/h] (approx.)
q_sensible =  round(1.08 * Q_Scfm * (Tdb - Tdb_room), 1)
# 8.) Latent Heat Gain [Btu/h] (approx.) 
q_latent = round(4840 * Q_Scfm * (w - W_room), 1)
# 9.) Total Heat Gain [Btu/h]
q_total = round(q_sensible + q_latent, 1)

# Format and write results to csv ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
output_headers = ["Q_Scfm", "Q_Acfm", "Velocity", "W", "q_sensible", "q_latent", "q_total"]
results = []
results.append(Q_Scfm)
results.append(Q_Acfm)
results.append(V)
results.append(w)
results.append(q_sensible)
results.append(q_latent)
results.append(q_total)
# results.append()
write_data(output_headers, "output.csv")
write_data(results, "output.csv")

