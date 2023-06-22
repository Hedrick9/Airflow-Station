import sys
import os
import csv
import time
from datetime import date, datetime
import labjack
import labjack_functions as ljf
import systemCalcs as calc
#______________________________________________________________________________
#
# Check for system inputs - If no system inputs provided, continue w/ main prompt
if len(sys.argv) > 1:
    # an argument was passed. The first argument specifies the user input.
    try:
        arg1 = int(sys.argv[1])
        if arg1 == 1:
            test = input("""What feature would you like to test?
        (1) Analog Input
        (2) Thermocouple\n""")
            arg2 = int(input("Positive Input Channel? (1, 2, 3, etc.)\n"))
            arg3 = int(input("Negative Input Channel if applicable? (199 for GND)\n"))
            arg4 = float(input("Voltage range if applicable?\n"))
            if test == '1':
                t_result = ljf.aiRead(arg2, arg3, arg4)
                print(t_result)
            elif test == '2':
                t_result = ljf.tempRead_TC(arg2, arg3)
            else:
                pass
        else:
            pass
    except:
        raise Exception("Invalid first argument \"{}\"".format(str(sys.argv[1])))
else:
    os.system('cls') # clear terminal screen: for linux/Mac - os.system('clear')
    arg1 = "None"
    start_input = input("""
                WELCOME TO THE BOOTLEG CKV PROGRAM!
                -----------------------------------
Of the options below, please select a test to begin:

(1) Idle Test (No Logging)
(2) Official Test (w/ Data Logging)

""")

    if start_input == '2': 

        # Create Data directory if not exist
        os.system('cls')
        os.chdir('..')
        current_directory = os.getcwd()
        if not os.path.exists(current_directory + '/Data'):
            os.mkdir(current_directory + '/Data')
            print('New Data directory added...\n')

        # Create unique data file
        os.chdir(current_directory + '/Data')
        file_letter = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
        file_date = date.today().strftime("%m-%d-%y")

        headers = ["Time of Day", "Test Time", "Tdb_Lab", "Tdb_room:", "Tdb_exh", 
                   "Tdew_room", "Tdew_exh", "Pbar_inHg", "Pdif_exh", "pp_water_supsys1", 
                   "pp_sat_supsys1", "pp_water_exh", "pp_sat_exh", "W_room", "W_exh", 
                   "rho_room", "rho_exh", "rh_room", "rh_exh", "V_exh", "Q_Acfm", 
                   "Q_Scfm", "Sensible HG", "Latent HG", "Total HG"]
        for i in range(len(file_letter)):
            if not os.path.isfile(os.getcwd() + '/' + file_date + file_letter[i] + ".csv"):
                file_name = file_date + file_letter[i] + ".csv"
                print("Adding new file: {}\n".format(file_name))
                break
            elif i == (len(file_letter)-1):
                file_name = input("Maximum default names achieved.\n User input file name:\n")+".csv"
                print("Adding new file: {}\n".format(file_name))

        with open(file_name, 'a') as file_data:
            csvWriter = csv.writer(file_data, delimiter=',')
            csvWriter.writerow([file_date])
            csvWriter.writerow(headers)

    elif start_input == '1':
        os.system('cls') # clear terminal screen: for linux/Mac - os.system('clear')
        print("Starting Idle Test...")

    else:
        print("A valid input was not provided.")

def write_data(file_name, data):
    with open(file_name, 'a', newline='') as f:
        csvWriter = csv.writer(f, delimiter=',')
        csvWriter.writerow(data)

###############################################################################
############### OFFICIAL TEST LOGGING SEQUENCE ################################
###############################################################################
test_time = 0
while True:
    tic = time.time()
    data = []
    # 1.) Timestamp
    tod = datetime.now()
    now = tod.strftime("%H:%M:%S")
    # 2.) Test Time
    test_time_min = round(test_time / 60, 2)
 
    try:
        # 3.) Room Dry Bulb Temperature
        T_room = ljf.tempRead_TC(6, 7, -3, 24)
        # 4.) Exhaust Dry Bulb Temperature
        T_exh = ljf.tempRead_TC(2, 3, 1)
        # 5.) Dew Point - Supply/Room
        Tdew_room = 51.8 #ljf.tempRead_TC(0, 1)
        # 6.) Dew Point - Exhaust
        Tdew_exh_mA = ljf.aiCurrent(11)[1] # (ch 11) Current -> Voltage using LJTick-Current Shunt
        Tdew_exh = round(calc.DP_DewTran(Tdew_exh_mA, -40, 60), 2) # (SigOUT, lo-range, hi-range in celsius)
        # 7.) Barometric Pressure
        Pbar_V = ljf.aiRead(12, 199, 5.0) # (channel 2, 199-GND, 5V Range) Setra Bar Press. Transducer
        Pbar = (80*Pbar_V + 798.95) # Barometric Pressure in mbar 
        Pbar_inHg = round(Pbar/33.864, 2)
        # 8.) Differential Pressure - Velocity Pressure
        pdiff_exh_mA = ljf.aiCurrent(10)[1] #(ch 10) Current -> Voltage using LJTick-Current Shunt
        pdiff_exh = round(calc.pdiff_setra(pdiff_exh_mA, 0, 0.5), 3) + 0.003 # + offset (SigOUT, lo-range, hi-range)
        #************ Calculate air flow, and psychrometrics *********************
        # 9.) Partial Pressure Water Vapor (Calculated)
        pp_water_supsys1 = calc.Pp(Tdew_room)
        # 10.) Saturation Partial Pressure (at Dry bulb Temp)
        pp_sat_supsys1 = calc.Pp(T_room)
        # 11.) Partial Pressure Water Vapor (Calculated)
        pp_water_exh = calc.Pp(Tdew_exh)
        # 12.) Saturation Partial Pressure (at Dry bulb Temp)
        pp_sat_exh = calc.Pp(T_exh)
        # 13.) Humidity Ratio - Supply/Room
        W_room = calc.W(Pbar_inHg, pp_water_supsys1)
        # 14.) Humidity Ratio - Exhaust
        W_exh = calc.W(Pbar_inHg, pp_water_exh)
        # 15.) Calculated Air Density - Room/Supply System 1
        rho_room = calc.rho(Pbar, T_room, W_room) 
        # 16.) Calculated Air Density - Exhaust
        rho_exh = calc.rho(Pbar, T_exh, W_exh)
        # 17.) Calculated %RH - Room/Supply System 1
        rh_room = calc.RH(pp_water_supsys1, pp_sat_supsys1)
        # 18.) Calculated %RH - Exhaust
        rh_exh = calc.RH(pp_water_exh, pp_sat_exh)
        # 19.) Air Velocity
        V_exh = calc.velocity(pdiff_exh, rho_exh)
        # 20.) Actual Measured Flow [Acfm] - 8in diameter (7.87 ID) duct for Starbucks Heat Gain Testing
        Q_Acfm = round(calc.QflowActual(V_exh, 7.87), 2)
        # 21.) Standard Air Corrected Flow [Scfm]
        Q_Scfm = round(calc.QflowStandard(Q_Acfm, Pbar_inHg, T_exh), 2)
        # 22.) Sensible Heat Gain [Btu/h] (approx.)
        q_sensible =  round(1.08 * Q_Scfm * (T_exh - T_room), 1)
        # 23.) Latent Heat Gain [Btu/h] (approx.) 
        q_latent = round(4840 * Q_Scfm * (W_exh - W_room), 1)
        # 24.) Total Heat Gain [Btu/h]
        q_total = round(q_sensible + q_latent, 1)
        # 25.) Lab Temp
        T_lab = ljf.tempRead_TC(0, 1)
    except labjack.ljm.ljm.LJMError:
        print("Your device has been disconnected. Please reconnect!")
        data.append(now)
        data.append(test_time_min)
        for i in range(23):
            data.append('OPEN')
    except Exception as e:
        print(e)
    else:    
        data.append(now)                # 0
        data.append(test_time_min)      # 1
        data.append(T_lab)              # 2
        data.append(T_room)             # 3
        data.append(T_exh)              # 4
        data.append(Tdew_room)          # 5
        data.append(Tdew_exh)           # 6
        data.append(Pbar_inHg)          # 7
        data.append(round(pdiff_exh,2)) # 8
        data.append(pp_water_supsys1)   # 9
        data.append(pp_sat_supsys1)     # 10
        data.append(pp_water_exh)       # 11
        data.append(pp_sat_exh)         # 12
        data.append(W_room)             # 13
        data.append(W_exh)              # 14
        data.append(rho_room)           # 15
        data.append(rho_exh)            # 16
        data.append(rh_room)            # 17
        data.append(rh_exh)             # 18
        data.append(V_exh)              # 19
        data.append(Q_Acfm)             # 20
        data.append(Q_Scfm)             # 21
        data.append(q_sensible)         # 22
        data.append(q_latent)           # 23
        data.append(q_total)            # 24

# ---- Write data to .csv file ----------
    if start_input == '2':
        try:
            write_data(file_name, data)
        except Exception as e:
            print(e)
    else: 
        pass
# ---------------------------------------
    test_time += 5
    toc = time.time()
    process_time = round(toc-tic, 3)

    print("""
    Time:               {}
    Test Time:          {} min 
    Process Time:       {} sec 
    Room Temp:          {} F
    Exhaust Temp:       {} F
    Room Dewpoint:      {} F
    Exh. Dewpoint:      {} F
    Barometric Press.:  {} inHg
    Velocity Press.:    {} inWc
    Exhaust Flow:       {} Acfm 
                        {} Scmf
    Sensible Heat Gain: {} Btu/h
    Latent Heat Gain:   {} Btu/h
    Total Heat Gain:    {} Btu/h
    """.format(data[0], data[1], process_time, data[3], data[4], data[5], data[6],
               data[7], data[8], data[20], data[21], data[22], data[23], data[24]))
    
    t_delay = 5 - process_time
    time.sleep(t_delay)



