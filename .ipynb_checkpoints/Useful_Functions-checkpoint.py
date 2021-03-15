### Useful Functions
import numpy as np
pi = np.pi

## NOT AN ACTUAL FUNCTION
# produces an FSR for a ring by sweeping wavelength and voltage
def FSR():
    voltage_range = np.arange(0,4,0.5)
    wavelength_range = np.arange(1539.77,1558.98,0.01)
    plt.figure(figsize=(15,10))
    for voltage in tq(voltage_range):
        h.set_voltage(ring,voltage)
        power_measurements = []
        for wavelength in wavelength_range:
            mytunics.laser_wavelength(wavelength)
            time.sleep(0.05)
            power_measurements.append(PM.measure())
        plt.plot(wavelength_range, power_measurements, marker = "x", linestyle=None)
        print(voltage)
        dictionary = dict(zip(wavelength_range, power_measurements))
        
        
## Functiion to calibrate the ring
# sweeps the voltage while measuring the power and finds where a dip in power occurs due to the light coupling into the MRR


## Function to find the FSR of the ring, by sweeping the wavelength
# sweeps the wavelength of the laser 

def Ring_WaveLength_Check(wavelength_range, ring, PM):
    power_measurements = []
    for wavelength in wavelength_range:
        mytunics.laser_wavelength(wavelength)
        time.sleep(0.05)
        power_measurements.append(PM.measure())
    plt.plot(wavelength_range, power_measurements, marker = "x", linestyle=None)
    plt.show()
    dictionary = dict(zip(wavelength_range, power_measurements))
    return dictionary

def Ring_Cal(voltage_range, ring, PM):
    power_measurements = []
    for voltage in tqdm(voltage_range):
        h.set_voltage(ring,voltage)
        time.sleep(0.2)
        power_measurements.append(PM.measure())
    plt.plot(voltage_range, power_measurements, marker = "x", linestyle=None)
    plt.xlabel("Voltage (V)")
    plt.ylabel("Power (dB/m)")
    plt.title(ring)
    plt.show()
    dictionary = dict(zip(voltage_range, power_measurements))
    return dictionary 

def auto_Ring_cal(Ring_volts):
    new_ring_volts = {}
    for ring_name, ring_voltage in Ring_volts.items(): 
        h.set_many_phases(ring_config[ring_name])
        time.sleep(0.5)
        voltage_range = np.arange(ring_voltage - 0.5, ring_voltage  +0.5, 0.002)
        results = Ring_Cal(voltage_range, ring_name, PMs[ring_name])
        new_ring_volts[ring_name] = min(results.keys(), key=(lambda k: results[k]))
        
    with open('Ring_Coulping_Voltage.csv', 'w') as f:  # Just use 'w' mode in 3.x
        w = csv.DictWriter(f, Ring_volts.keys())
        w.writeheader()
        w.writerow(Ring_volts)
    return new_ring_volts

ring_config_dict = {"MRR1":{"BS1":pi,
    "BS2":0,
    "WDM1":pi/2,
    "Prj_RY1":pi},
              "MRR2":{ "BS1":pi,
    "BS2":pi,
    "WDM2":pi/2,
    "Prj_RY1":pi},
              "MRR3":{ "BS1":0,
    "BS3":pi,
    "WDM3":pi/2,
    "Prj_RY4":pi,
    "Ctr_1":0},
              "MRR4":{ "BS1":0,
    "BS3":0,
    "WDM4":pi/2,
    "Prj_RY4":0},
    "Ctr_2":0}

def Save_to_CSV(results, filename):
    with open(filename, 'w') as f:  # Just use 'w' mode in 3.x
        w = csv.DictWriter(f, results.keys())
        w.writeheader()
        w.writerow(results)
